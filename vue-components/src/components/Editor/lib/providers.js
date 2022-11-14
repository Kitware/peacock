import { INITIAL, Registry, parseRawGrammar } from 'vscode-textmate';
// @ts-ignore
import { generateTokensCSSForColorMap } from 'monaco-editor/esm/vs/editor/common/modes/supports/tokenization.js';
// @ts-ignore
import { TokenizationRegistry } from 'monaco-editor/esm/vs/editor/common/modes.js';
// @ts-ignore
import { Color } from 'monaco-editor/esm/vs/base/common/color.js';
/**
 * Basic provider to implement the fetchLanguageInfo() function needed to
 * power registerLanguages(). It is designed to fetch all resources
 * asynchronously based on a simple layout of static resources on the server.
 */
export class SimpleLanguageInfoProvider {
    constructor(config) {
        this.config = config;
        const { grammars, fetchGrammar, theme, onigLib, monaco } = config;
        this.monaco = monaco;
        this.registry = new Registry({
            onigLib,
            async loadGrammar(scopeName) {
                const scopeNameInfo = grammars[scopeName];
                if (scopeNameInfo == null) {
                    return null;
                }
                const { type, grammar } = await fetchGrammar(scopeName);
                // If this is a JSON grammar, filePath must be specified with a `.json`
                // file extension or else parseRawGrammar() will assume it is a PLIST
                // grammar.
                return parseRawGrammar(grammar, `example.${type}`);
            },
            /**
             * For the given scope, returns a list of additional grammars that should be
             * "injected into" it (i.e., a list of grammars that want to extend the
             * specified `scopeName`). The most common example is other grammars that
             * want to "inject themselves" into the `text.html.markdown` scope so they
             * can be used with fenced code blocks.
             *
             * In the manifest of a VS Code extension, a grammar signals that it wants
             * to do this via the "injectTo" property:
             * https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide#injection-grammars
             */
            getInjections(scopeName) {
                const grammar = grammars[scopeName];
                return grammar ? grammar.injections : undefined;
            },
            // Note that nothing will display without the theme!
            theme,
        });
        this.tokensProviderCache = new TokensProviderCache(this.registry);
    }
    /**
     * Be sure this is done after Monaco injects its default styles so that the
     * injected CSS overrides the defaults.
     */
    async injectCSS() {
        const cssColors = await this.registry.getColorMap();
        const colorMap = await cssColors.map(Color.Format.CSS.parseHex);
        // This is needed to ensure the minimap gets the right colors.
        await TokenizationRegistry.setColorMap(colorMap);
        const css = await generateTokensCSSForColorMap(colorMap);
        const style = await createStyleElementForColorsCSS();
        style.innerHTML = css;
    }
    async fetchLanguageInfo(language) {
        const [tokensProvider, configuration] = await Promise.all([
            this.getTokensProviderForLanguage(language),
            this.config.fetchConfiguration(language),
        ]);
        return { tokensProvider, configuration };
    }
    getTokensProviderForLanguage(language) {
        const scopeName = this.getScopeNameForLanguage(language);
        if (scopeName == null) {
            return Promise.resolve(null);
        }
        const encodedLanguageId = this.monaco.languages.getEncodedLanguageId(language);
        // Ensure the result of createEncodedTokensProvider() is resolved before
        // setting the language configuration.
        return this.tokensProviderCache.createEncodedTokensProvider(scopeName, encodedLanguageId);
    }
    getScopeNameForLanguage(language) {
        for (const [scopeName, grammar] of Object.entries(this.config.grammars)) {
            if (grammar.language === language) {
                return scopeName;
            }
        }
        return null;
    }
}
class TokensProviderCache {
    constructor(registry) {
        this.registry = registry;
        this.scopeNameToGrammar = new Map();
    }
    async createEncodedTokensProvider(scopeName, encodedLanguageId) {
        const grammar = await this.getGrammar(scopeName, encodedLanguageId);
        return {
            getInitialState() {
                return INITIAL;
            },
            tokenizeEncoded(line, state) {
                const tokenizeLineResult2 = grammar.tokenizeLine2(line, state);
                const { tokens, ruleStack: endState } = tokenizeLineResult2;
                return { tokens, endState };
            },
        };
    }
    getGrammar(scopeName, encodedLanguageId) {
        const grammar = this.scopeNameToGrammar.get(scopeName);
        if (grammar != null) {
            return grammar;
        }
        // This is defined in vscode-textmate and has optional embeddedLanguages
        // and tokenTypes fields that might be useful/necessary to take advantage of
        // at some point.
        const grammarConfiguration = {};
        // We use loadGrammarWithConfiguration() rather than loadGrammar() because
        // we discovered that if the numeric LanguageId is not specified, then it
        // does not get encoded in the TokenMetadata.
        //
        // Failure to do so means that the LanguageId cannot be read back later,
        // which can cause other Monaco features, such as "Toggle Line Comment",
        // to fail.
        const promise = this.registry
            .loadGrammarWithConfiguration(scopeName, encodedLanguageId, grammarConfiguration)
            .then((grammar) => {
            if (grammar) {
                return grammar;
            }
            else {
                throw Error(`failed to load grammar for ${scopeName}`);
            }
        });
        this.scopeNameToGrammar.set(scopeName, promise);
        return promise;
    }
}
function createStyleElementForColorsCSS() {
    var _a;
    // We want to ensure that our <style> element appears after Monaco's so that
    // we can override some styles it inserted for the default theme.
    const style = document.createElement('style');
    // We expect the styles we need to override to be in an element with the class
    // name 'monaco-colors' based on:
    // https://github.com/microsoft/vscode/blob/f78d84606cd16d75549c82c68888de91d8bdec9f/src/vs/editor/standalone/browser/standaloneThemeServiceImpl.ts#L206-L214
    const monacoColors = document.getElementsByClassName('monaco-colors')[0];
    if (monacoColors) {
        (_a = monacoColors.parentElement) === null || _a === void 0 ? void 0 : _a.insertBefore(style, monacoColors.nextSibling);
    }
    else {
        // Though if we cannot find it, just append to <head>.
        let { head } = document;
        if (head == null) {
            head = document.getElementsByTagName('head')[0];
        }
        head === null || head === void 0 ? void 0 : head.appendChild(style);
    }
    return style;
}
