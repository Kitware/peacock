((typeof self !== 'undefined' ? self : this)["webpackJsonppeacock_trame"] = (typeof self !== 'undefined' ? self : this)["webpackJsonppeacock_trame"] || []).push([[80],{

/***/ "e328":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
// ESM COMPAT FLAG
__webpack_require__.r(__webpack_exports__);

// EXPORTS
__webpack_require__.d(__webpack_exports__, "setupTypeScript", function() { return /* binding */ setupTypeScript; });
__webpack_require__.d(__webpack_exports__, "setupJavaScript", function() { return /* binding */ setupJavaScript; });
__webpack_require__.d(__webpack_exports__, "getJavaScriptWorker", function() { return /* binding */ getJavaScriptWorker; });
__webpack_require__.d(__webpack_exports__, "getTypeScriptWorker", function() { return /* binding */ getTypeScriptWorker; });

// EXTERNAL MODULE: ./node_modules/monaco-editor/esm/vs/language/typescript/fillers/monaco-editor-core.js
var monaco_editor_core = __webpack_require__("bf44");

// CONCATENATED MODULE: ./node_modules/monaco-editor/esm/vs/language/typescript/workerManager.js
/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (undefined && undefined.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};

var workerManager_WorkerManager = /** @class */ (function () {
    function WorkerManager(modeId, defaults) {
        var _this = this;
        this._modeId = modeId;
        this._defaults = defaults;
        this._worker = null;
        this._client = null;
        this._configChangeListener = this._defaults.onDidChange(function () { return _this._stopWorker(); });
        this._updateExtraLibsToken = 0;
        this._extraLibsChangeListener = this._defaults.onDidExtraLibsChange(function () {
            return _this._updateExtraLibs();
        });
    }
    WorkerManager.prototype._stopWorker = function () {
        if (this._worker) {
            this._worker.dispose();
            this._worker = null;
        }
        this._client = null;
    };
    WorkerManager.prototype.dispose = function () {
        this._configChangeListener.dispose();
        this._extraLibsChangeListener.dispose();
        this._stopWorker();
    };
    WorkerManager.prototype._updateExtraLibs = function () {
        return __awaiter(this, void 0, void 0, function () {
            var myToken, proxy;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!this._worker) {
                            return [2 /*return*/];
                        }
                        myToken = ++this._updateExtraLibsToken;
                        return [4 /*yield*/, this._worker.getProxy()];
                    case 1:
                        proxy = _a.sent();
                        if (this._updateExtraLibsToken !== myToken) {
                            // avoid multiple calls
                            return [2 /*return*/];
                        }
                        proxy.updateExtraLibs(this._defaults.getExtraLibs());
                        return [2 /*return*/];
                }
            });
        });
    };
    WorkerManager.prototype._getClient = function () {
        var _this = this;
        if (!this._client) {
            this._worker = monaco_editor_core["editor"].createWebWorker({
                // module that exports the create() method and returns a `TypeScriptWorker` instance
                moduleId: 'vs/language/typescript/tsWorker',
                label: this._modeId,
                keepIdleModels: true,
                // passed in to the create() method
                createData: {
                    compilerOptions: this._defaults.getCompilerOptions(),
                    extraLibs: this._defaults.getExtraLibs(),
                    customWorkerPath: this._defaults.workerOptions.customWorkerPath,
                    inlayHintsOptions: this._defaults.inlayHintsOptions
                }
            });
            var p = this._worker.getProxy();
            if (this._defaults.getEagerModelSync()) {
                p = p.then(function (worker) {
                    if (_this._worker) {
                        return _this._worker.withSyncedResources(monaco_editor_core["editor"]
                            .getModels()
                            .filter(function (model) { return model.getLanguageId() === _this._modeId; })
                            .map(function (model) { return model.uri; }));
                    }
                    return worker;
                });
            }
            this._client = p;
        }
        return this._client;
    };
    WorkerManager.prototype.getLanguageServiceWorker = function () {
        var _this = this;
        var resources = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            resources[_i] = arguments[_i];
        }
        var _client;
        return this._getClient()
            .then(function (client) {
            _client = client;
        })
            .then(function (_) {
            if (_this._worker) {
                return _this._worker.withSyncedResources(resources);
            }
        })
            .then(function (_) { return _client; });
    };
    return WorkerManager;
}());


// EXTERNAL MODULE: ./node_modules/monaco-editor/esm/vs/language/typescript/monaco.contribution.js + 1 modules
var monaco_contribution = __webpack_require__("cf78");

// CONCATENATED MODULE: ./node_modules/monaco-editor/esm/vs/language/typescript/lib/lib.index.js
/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
//
// **NOTE**: Do not edit directly! This file is generated using `npm run import-typescript`
//
/** Contains all the lib files */
var libFileSet = {};
libFileSet['lib.d.ts'] = true;
libFileSet['lib.dom.d.ts'] = true;
libFileSet['lib.dom.iterable.d.ts'] = true;
libFileSet['lib.es2015.collection.d.ts'] = true;
libFileSet['lib.es2015.core.d.ts'] = true;
libFileSet['lib.es2015.d.ts'] = true;
libFileSet['lib.es2015.generator.d.ts'] = true;
libFileSet['lib.es2015.iterable.d.ts'] = true;
libFileSet['lib.es2015.promise.d.ts'] = true;
libFileSet['lib.es2015.proxy.d.ts'] = true;
libFileSet['lib.es2015.reflect.d.ts'] = true;
libFileSet['lib.es2015.symbol.d.ts'] = true;
libFileSet['lib.es2015.symbol.wellknown.d.ts'] = true;
libFileSet['lib.es2016.array.include.d.ts'] = true;
libFileSet['lib.es2016.d.ts'] = true;
libFileSet['lib.es2016.full.d.ts'] = true;
libFileSet['lib.es2017.d.ts'] = true;
libFileSet['lib.es2017.full.d.ts'] = true;
libFileSet['lib.es2017.intl.d.ts'] = true;
libFileSet['lib.es2017.object.d.ts'] = true;
libFileSet['lib.es2017.sharedmemory.d.ts'] = true;
libFileSet['lib.es2017.string.d.ts'] = true;
libFileSet['lib.es2017.typedarrays.d.ts'] = true;
libFileSet['lib.es2018.asyncgenerator.d.ts'] = true;
libFileSet['lib.es2018.asynciterable.d.ts'] = true;
libFileSet['lib.es2018.d.ts'] = true;
libFileSet['lib.es2018.full.d.ts'] = true;
libFileSet['lib.es2018.intl.d.ts'] = true;
libFileSet['lib.es2018.promise.d.ts'] = true;
libFileSet['lib.es2018.regexp.d.ts'] = true;
libFileSet['lib.es2019.array.d.ts'] = true;
libFileSet['lib.es2019.d.ts'] = true;
libFileSet['lib.es2019.full.d.ts'] = true;
libFileSet['lib.es2019.object.d.ts'] = true;
libFileSet['lib.es2019.string.d.ts'] = true;
libFileSet['lib.es2019.symbol.d.ts'] = true;
libFileSet['lib.es2020.bigint.d.ts'] = true;
libFileSet['lib.es2020.d.ts'] = true;
libFileSet['lib.es2020.full.d.ts'] = true;
libFileSet['lib.es2020.intl.d.ts'] = true;
libFileSet['lib.es2020.promise.d.ts'] = true;
libFileSet['lib.es2020.sharedmemory.d.ts'] = true;
libFileSet['lib.es2020.string.d.ts'] = true;
libFileSet['lib.es2020.symbol.wellknown.d.ts'] = true;
libFileSet['lib.es2021.d.ts'] = true;
libFileSet['lib.es2021.full.d.ts'] = true;
libFileSet['lib.es2021.promise.d.ts'] = true;
libFileSet['lib.es2021.string.d.ts'] = true;
libFileSet['lib.es2021.weakref.d.ts'] = true;
libFileSet['lib.es5.d.ts'] = true;
libFileSet['lib.es6.d.ts'] = true;
libFileSet['lib.esnext.d.ts'] = true;
libFileSet['lib.esnext.full.d.ts'] = true;
libFileSet['lib.esnext.intl.d.ts'] = true;
libFileSet['lib.esnext.promise.d.ts'] = true;
libFileSet['lib.esnext.string.d.ts'] = true;
libFileSet['lib.esnext.weakref.d.ts'] = true;
libFileSet['lib.scripthost.d.ts'] = true;
libFileSet['lib.webworker.d.ts'] = true;
libFileSet['lib.webworker.importscripts.d.ts'] = true;
libFileSet['lib.webworker.iterable.d.ts'] = true;

// CONCATENATED MODULE: ./node_modules/monaco-editor/esm/vs/language/typescript/languageFeatures.js
/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

var __extends = (undefined && undefined.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __assign = (undefined && undefined.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var languageFeatures_awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var languageFeatures_generator = (undefined && undefined.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};



//#region utils copied from typescript to prevent loading the entire typescriptServices ---
var IndentStyle;
(function (IndentStyle) {
    IndentStyle[IndentStyle["None"] = 0] = "None";
    IndentStyle[IndentStyle["Block"] = 1] = "Block";
    IndentStyle[IndentStyle["Smart"] = 2] = "Smart";
})(IndentStyle || (IndentStyle = {}));
function flattenDiagnosticMessageText(diag, newLine, indent) {
    if (indent === void 0) { indent = 0; }
    if (typeof diag === 'string') {
        return diag;
    }
    else if (diag === undefined) {
        return '';
    }
    var result = '';
    if (indent) {
        result += newLine;
        for (var i = 0; i < indent; i++) {
            result += '  ';
        }
    }
    result += diag.messageText;
    indent++;
    if (diag.next) {
        for (var _i = 0, _a = diag.next; _i < _a.length; _i++) {
            var kid = _a[_i];
            result += flattenDiagnosticMessageText(kid, newLine, indent);
        }
    }
    return result;
}
function displayPartsToString(displayParts) {
    if (displayParts) {
        return displayParts.map(function (displayPart) { return displayPart.text; }).join('');
    }
    return '';
}
//#endregion
var Adapter = /** @class */ (function () {
    function Adapter(_worker) {
        this._worker = _worker;
    }
    // protected _positionToOffset(model: editor.ITextModel, position: monaco.IPosition): number {
    // 	return model.getOffsetAt(position);
    // }
    // protected _offsetToPosition(model: editor.ITextModel, offset: number): monaco.IPosition {
    // 	return model.getPositionAt(offset);
    // }
    Adapter.prototype._textSpanToRange = function (model, span) {
        var p1 = model.getPositionAt(span.start);
        var p2 = model.getPositionAt(span.start + span.length);
        var startLineNumber = p1.lineNumber, startColumn = p1.column;
        var endLineNumber = p2.lineNumber, endColumn = p2.column;
        return { startLineNumber: startLineNumber, startColumn: startColumn, endLineNumber: endLineNumber, endColumn: endColumn };
    };
    return Adapter;
}());

// --- lib files
var languageFeatures_LibFiles = /** @class */ (function () {
    function LibFiles(_worker) {
        this._worker = _worker;
        this._libFiles = {};
        this._hasFetchedLibFiles = false;
        this._fetchLibFilesPromise = null;
    }
    LibFiles.prototype.isLibFile = function (uri) {
        if (!uri) {
            return false;
        }
        if (uri.path.indexOf('/lib.') === 0) {
            return !!libFileSet[uri.path.slice(1)];
        }
        return false;
    };
    LibFiles.prototype.getOrCreateModel = function (fileName) {
        var uri = monaco_editor_core["Uri"].parse(fileName);
        var model = monaco_editor_core["editor"].getModel(uri);
        if (model) {
            return model;
        }
        if (this.isLibFile(uri) && this._hasFetchedLibFiles) {
            return monaco_editor_core["editor"].createModel(this._libFiles[uri.path.slice(1)], 'typescript', uri);
        }
        var matchedLibFile = monaco_contribution["a" /* typescriptDefaults */].getExtraLibs()[fileName];
        if (matchedLibFile) {
            return monaco_editor_core["editor"].createModel(matchedLibFile.content, 'typescript', uri);
        }
        return null;
    };
    LibFiles.prototype._containsLibFile = function (uris) {
        for (var _i = 0, uris_1 = uris; _i < uris_1.length; _i++) {
            var uri = uris_1[_i];
            if (this.isLibFile(uri)) {
                return true;
            }
        }
        return false;
    };
    LibFiles.prototype.fetchLibFilesIfNecessary = function (uris) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!this._containsLibFile(uris)) {
                            // no lib files necessary
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, this._fetchLibFiles()];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    LibFiles.prototype._fetchLibFiles = function () {
        var _this = this;
        if (!this._fetchLibFilesPromise) {
            this._fetchLibFilesPromise = this._worker()
                .then(function (w) { return w.getLibFiles(); })
                .then(function (libFiles) {
                _this._hasFetchedLibFiles = true;
                _this._libFiles = libFiles;
            });
        }
        return this._fetchLibFilesPromise;
    };
    return LibFiles;
}());

// --- diagnostics --- ---
var DiagnosticCategory;
(function (DiagnosticCategory) {
    DiagnosticCategory[DiagnosticCategory["Warning"] = 0] = "Warning";
    DiagnosticCategory[DiagnosticCategory["Error"] = 1] = "Error";
    DiagnosticCategory[DiagnosticCategory["Suggestion"] = 2] = "Suggestion";
    DiagnosticCategory[DiagnosticCategory["Message"] = 3] = "Message";
})(DiagnosticCategory || (DiagnosticCategory = {}));
var languageFeatures_DiagnosticsAdapter = /** @class */ (function (_super) {
    __extends(DiagnosticsAdapter, _super);
    function DiagnosticsAdapter(_libFiles, _defaults, _selector, worker) {
        var _this = _super.call(this, worker) || this;
        _this._libFiles = _libFiles;
        _this._defaults = _defaults;
        _this._selector = _selector;
        _this._disposables = [];
        _this._listener = Object.create(null);
        var onModelAdd = function (model) {
            if (model.getLanguageId() !== _selector) {
                return;
            }
            var maybeValidate = function () {
                var onlyVisible = _this._defaults.getDiagnosticsOptions().onlyVisible;
                if (onlyVisible) {
                    if (model.isAttachedToEditor()) {
                        _this._doValidate(model);
                    }
                }
                else {
                    _this._doValidate(model);
                }
            };
            var handle;
            var changeSubscription = model.onDidChangeContent(function () {
                clearTimeout(handle);
                handle = setTimeout(maybeValidate, 500);
            });
            var visibleSubscription = model.onDidChangeAttached(function () {
                var onlyVisible = _this._defaults.getDiagnosticsOptions().onlyVisible;
                if (onlyVisible) {
                    if (model.isAttachedToEditor()) {
                        // this model is now attached to an editor
                        // => compute diagnostics
                        maybeValidate();
                    }
                    else {
                        // this model is no longer attached to an editor
                        // => clear existing diagnostics
                        monaco_editor_core["editor"].setModelMarkers(model, _this._selector, []);
                    }
                }
            });
            _this._listener[model.uri.toString()] = {
                dispose: function () {
                    changeSubscription.dispose();
                    visibleSubscription.dispose();
                    clearTimeout(handle);
                }
            };
            maybeValidate();
        };
        var onModelRemoved = function (model) {
            monaco_editor_core["editor"].setModelMarkers(model, _this._selector, []);
            var key = model.uri.toString();
            if (_this._listener[key]) {
                _this._listener[key].dispose();
                delete _this._listener[key];
            }
        };
        _this._disposables.push(monaco_editor_core["editor"].onDidCreateModel(function (model) { return onModelAdd(model); }));
        _this._disposables.push(monaco_editor_core["editor"].onWillDisposeModel(onModelRemoved));
        _this._disposables.push(monaco_editor_core["editor"].onDidChangeModelLanguage(function (event) {
            onModelRemoved(event.model);
            onModelAdd(event.model);
        }));
        _this._disposables.push({
            dispose: function () {
                for (var _i = 0, _a = monaco_editor_core["editor"].getModels(); _i < _a.length; _i++) {
                    var model = _a[_i];
                    onModelRemoved(model);
                }
            }
        });
        var recomputeDiagostics = function () {
            // redo diagnostics when options change
            for (var _i = 0, _a = monaco_editor_core["editor"].getModels(); _i < _a.length; _i++) {
                var model = _a[_i];
                onModelRemoved(model);
                onModelAdd(model);
            }
        };
        _this._disposables.push(_this._defaults.onDidChange(recomputeDiagostics));
        _this._disposables.push(_this._defaults.onDidExtraLibsChange(recomputeDiagostics));
        monaco_editor_core["editor"].getModels().forEach(function (model) { return onModelAdd(model); });
        return _this;
    }
    DiagnosticsAdapter.prototype.dispose = function () {
        this._disposables.forEach(function (d) { return d && d.dispose(); });
        this._disposables = [];
    };
    DiagnosticsAdapter.prototype._doValidate = function (model) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var worker, promises, _a, noSyntaxValidation, noSemanticValidation, noSuggestionDiagnostics, allDiagnostics, diagnostics, relatedUris;
            var _this = this;
            return languageFeatures_generator(this, function (_b) {
                switch (_b.label) {
                    case 0: return [4 /*yield*/, this._worker(model.uri)];
                    case 1:
                        worker = _b.sent();
                        if (model.isDisposed()) {
                            // model was disposed in the meantime
                            return [2 /*return*/];
                        }
                        promises = [];
                        _a = this._defaults.getDiagnosticsOptions(), noSyntaxValidation = _a.noSyntaxValidation, noSemanticValidation = _a.noSemanticValidation, noSuggestionDiagnostics = _a.noSuggestionDiagnostics;
                        if (!noSyntaxValidation) {
                            promises.push(worker.getSyntacticDiagnostics(model.uri.toString()));
                        }
                        if (!noSemanticValidation) {
                            promises.push(worker.getSemanticDiagnostics(model.uri.toString()));
                        }
                        if (!noSuggestionDiagnostics) {
                            promises.push(worker.getSuggestionDiagnostics(model.uri.toString()));
                        }
                        return [4 /*yield*/, Promise.all(promises)];
                    case 2:
                        allDiagnostics = _b.sent();
                        if (!allDiagnostics || model.isDisposed()) {
                            // model was disposed in the meantime
                            return [2 /*return*/];
                        }
                        diagnostics = allDiagnostics
                            .reduce(function (p, c) { return c.concat(p); }, [])
                            .filter(function (d) {
                            return (_this._defaults.getDiagnosticsOptions().diagnosticCodesToIgnore || []).indexOf(d.code) ===
                                -1;
                        });
                        relatedUris = diagnostics
                            .map(function (d) { return d.relatedInformation || []; })
                            .reduce(function (p, c) { return c.concat(p); }, [])
                            .map(function (relatedInformation) {
                            return relatedInformation.file ? monaco_editor_core["Uri"].parse(relatedInformation.file.fileName) : null;
                        });
                        return [4 /*yield*/, this._libFiles.fetchLibFilesIfNecessary(relatedUris)];
                    case 3:
                        _b.sent();
                        if (model.isDisposed()) {
                            // model was disposed in the meantime
                            return [2 /*return*/];
                        }
                        monaco_editor_core["editor"].setModelMarkers(model, this._selector, diagnostics.map(function (d) { return _this._convertDiagnostics(model, d); }));
                        return [2 /*return*/];
                }
            });
        });
    };
    DiagnosticsAdapter.prototype._convertDiagnostics = function (model, diag) {
        var diagStart = diag.start || 0;
        var diagLength = diag.length || 1;
        var _a = model.getPositionAt(diagStart), startLineNumber = _a.lineNumber, startColumn = _a.column;
        var _b = model.getPositionAt(diagStart + diagLength), endLineNumber = _b.lineNumber, endColumn = _b.column;
        var tags = [];
        if (diag.reportsUnnecessary) {
            tags.push(monaco_editor_core["MarkerTag"].Unnecessary);
        }
        if (diag.reportsDeprecated) {
            tags.push(monaco_editor_core["MarkerTag"].Deprecated);
        }
        return {
            severity: this._tsDiagnosticCategoryToMarkerSeverity(diag.category),
            startLineNumber: startLineNumber,
            startColumn: startColumn,
            endLineNumber: endLineNumber,
            endColumn: endColumn,
            message: flattenDiagnosticMessageText(diag.messageText, '\n'),
            code: diag.code.toString(),
            tags: tags,
            relatedInformation: this._convertRelatedInformation(model, diag.relatedInformation)
        };
    };
    DiagnosticsAdapter.prototype._convertRelatedInformation = function (model, relatedInformation) {
        var _this = this;
        if (!relatedInformation) {
            return [];
        }
        var result = [];
        relatedInformation.forEach(function (info) {
            var relatedResource = model;
            if (info.file) {
                relatedResource = _this._libFiles.getOrCreateModel(info.file.fileName);
            }
            if (!relatedResource) {
                return;
            }
            var infoStart = info.start || 0;
            var infoLength = info.length || 1;
            var _a = relatedResource.getPositionAt(infoStart), startLineNumber = _a.lineNumber, startColumn = _a.column;
            var _b = relatedResource.getPositionAt(infoStart + infoLength), endLineNumber = _b.lineNumber, endColumn = _b.column;
            result.push({
                resource: relatedResource.uri,
                startLineNumber: startLineNumber,
                startColumn: startColumn,
                endLineNumber: endLineNumber,
                endColumn: endColumn,
                message: flattenDiagnosticMessageText(info.messageText, '\n')
            });
        });
        return result;
    };
    DiagnosticsAdapter.prototype._tsDiagnosticCategoryToMarkerSeverity = function (category) {
        switch (category) {
            case DiagnosticCategory.Error:
                return monaco_editor_core["MarkerSeverity"].Error;
            case DiagnosticCategory.Message:
                return monaco_editor_core["MarkerSeverity"].Info;
            case DiagnosticCategory.Warning:
                return monaco_editor_core["MarkerSeverity"].Warning;
            case DiagnosticCategory.Suggestion:
                return monaco_editor_core["MarkerSeverity"].Hint;
        }
        return monaco_editor_core["MarkerSeverity"].Info;
    };
    return DiagnosticsAdapter;
}(Adapter));

var languageFeatures_SuggestAdapter = /** @class */ (function (_super) {
    __extends(SuggestAdapter, _super);
    function SuggestAdapter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(SuggestAdapter.prototype, "triggerCharacters", {
        get: function () {
            return ['.'];
        },
        enumerable: false,
        configurable: true
    });
    SuggestAdapter.prototype.provideCompletionItems = function (model, position, _context, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var wordInfo, wordRange, resource, offset, worker, info, suggestions;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        wordInfo = model.getWordUntilPosition(position);
                        wordRange = new monaco_editor_core["Range"](position.lineNumber, wordInfo.startColumn, position.lineNumber, wordInfo.endColumn);
                        resource = model.uri;
                        offset = model.getOffsetAt(position);
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getCompletionsAtPosition(resource.toString(), offset)];
                    case 2:
                        info = _a.sent();
                        if (!info || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        suggestions = info.entries.map(function (entry) {
                            var _a;
                            var range = wordRange;
                            if (entry.replacementSpan) {
                                var p1 = model.getPositionAt(entry.replacementSpan.start);
                                var p2 = model.getPositionAt(entry.replacementSpan.start + entry.replacementSpan.length);
                                range = new monaco_editor_core["Range"](p1.lineNumber, p1.column, p2.lineNumber, p2.column);
                            }
                            var tags = [];
                            if (((_a = entry.kindModifiers) === null || _a === void 0 ? void 0 : _a.indexOf('deprecated')) !== -1) {
                                tags.push(monaco_editor_core["languages"].CompletionItemTag.Deprecated);
                            }
                            return {
                                uri: resource,
                                position: position,
                                offset: offset,
                                range: range,
                                label: entry.name,
                                insertText: entry.name,
                                sortText: entry.sortText,
                                kind: SuggestAdapter.convertKind(entry.kind),
                                tags: tags
                            };
                        });
                        return [2 /*return*/, {
                                suggestions: suggestions
                            }];
                }
            });
        });
    };
    SuggestAdapter.prototype.resolveCompletionItem = function (item, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var myItem, resource, position, offset, worker, details;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        myItem = item;
                        resource = myItem.uri;
                        position = myItem.position;
                        offset = myItem.offset;
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        return [4 /*yield*/, worker.getCompletionEntryDetails(resource.toString(), offset, myItem.label)];
                    case 2:
                        details = _a.sent();
                        if (!details) {
                            return [2 /*return*/, myItem];
                        }
                        return [2 /*return*/, {
                                uri: resource,
                                position: position,
                                label: details.name,
                                kind: SuggestAdapter.convertKind(details.kind),
                                detail: displayPartsToString(details.displayParts),
                                documentation: {
                                    value: SuggestAdapter.createDocumentationString(details)
                                }
                            }];
                }
            });
        });
    };
    SuggestAdapter.convertKind = function (kind) {
        switch (kind) {
            case Kind.primitiveType:
            case Kind.keyword:
                return monaco_editor_core["languages"].CompletionItemKind.Keyword;
            case Kind.variable:
            case Kind.localVariable:
                return monaco_editor_core["languages"].CompletionItemKind.Variable;
            case Kind.memberVariable:
            case Kind.memberGetAccessor:
            case Kind.memberSetAccessor:
                return monaco_editor_core["languages"].CompletionItemKind.Field;
            case Kind.function:
            case Kind.memberFunction:
            case Kind.constructSignature:
            case Kind.callSignature:
            case Kind.indexSignature:
                return monaco_editor_core["languages"].CompletionItemKind.Function;
            case Kind.enum:
                return monaco_editor_core["languages"].CompletionItemKind.Enum;
            case Kind.module:
                return monaco_editor_core["languages"].CompletionItemKind.Module;
            case Kind.class:
                return monaco_editor_core["languages"].CompletionItemKind.Class;
            case Kind.interface:
                return monaco_editor_core["languages"].CompletionItemKind.Interface;
            case Kind.warning:
                return monaco_editor_core["languages"].CompletionItemKind.File;
        }
        return monaco_editor_core["languages"].CompletionItemKind.Property;
    };
    SuggestAdapter.createDocumentationString = function (details) {
        var documentationString = displayPartsToString(details.documentation);
        if (details.tags) {
            for (var _i = 0, _a = details.tags; _i < _a.length; _i++) {
                var tag = _a[_i];
                documentationString += "\n\n" + tagToString(tag);
            }
        }
        return documentationString;
    };
    return SuggestAdapter;
}(Adapter));

function tagToString(tag) {
    var tagLabel = "*@" + tag.name + "*";
    if (tag.name === 'param' && tag.text) {
        var _a = tag.text, paramName = _a[0], rest = _a.slice(1);
        tagLabel += "`" + paramName.text + "`";
        if (rest.length > 0)
            tagLabel += " \u2014 " + rest.map(function (r) { return r.text; }).join(' ');
    }
    else if (Array.isArray(tag.text)) {
        tagLabel += " \u2014 " + tag.text.map(function (r) { return r.text; }).join(' ');
    }
    else if (tag.text) {
        tagLabel += " \u2014 " + tag.text;
    }
    return tagLabel;
}
var languageFeatures_SignatureHelpAdapter = /** @class */ (function (_super) {
    __extends(SignatureHelpAdapter, _super);
    function SignatureHelpAdapter() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.signatureHelpTriggerCharacters = ['(', ','];
        return _this;
    }
    SignatureHelpAdapter._toSignatureHelpTriggerReason = function (context) {
        switch (context.triggerKind) {
            case monaco_editor_core["languages"].SignatureHelpTriggerKind.TriggerCharacter:
                if (context.triggerCharacter) {
                    if (context.isRetrigger) {
                        return { kind: 'retrigger', triggerCharacter: context.triggerCharacter };
                    }
                    else {
                        return { kind: 'characterTyped', triggerCharacter: context.triggerCharacter };
                    }
                }
                else {
                    return { kind: 'invoked' };
                }
            case monaco_editor_core["languages"].SignatureHelpTriggerKind.ContentChange:
                return context.isRetrigger ? { kind: 'retrigger' } : { kind: 'invoked' };
            case monaco_editor_core["languages"].SignatureHelpTriggerKind.Invoke:
            default:
                return { kind: 'invoked' };
        }
    };
    SignatureHelpAdapter.prototype.provideSignatureHelp = function (model, position, token, context) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, offset, worker, info, ret;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        offset = model.getOffsetAt(position);
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getSignatureHelpItems(resource.toString(), offset, {
                                triggerReason: SignatureHelpAdapter._toSignatureHelpTriggerReason(context)
                            })];
                    case 2:
                        info = _a.sent();
                        if (!info || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        ret = {
                            activeSignature: info.selectedItemIndex,
                            activeParameter: info.argumentIndex,
                            signatures: []
                        };
                        info.items.forEach(function (item) {
                            var signature = {
                                label: '',
                                parameters: []
                            };
                            signature.documentation = {
                                value: displayPartsToString(item.documentation)
                            };
                            signature.label += displayPartsToString(item.prefixDisplayParts);
                            item.parameters.forEach(function (p, i, a) {
                                var label = displayPartsToString(p.displayParts);
                                var parameter = {
                                    label: label,
                                    documentation: {
                                        value: displayPartsToString(p.documentation)
                                    }
                                };
                                signature.label += label;
                                signature.parameters.push(parameter);
                                if (i < a.length - 1) {
                                    signature.label += displayPartsToString(item.separatorDisplayParts);
                                }
                            });
                            signature.label += displayPartsToString(item.suffixDisplayParts);
                            ret.signatures.push(signature);
                        });
                        return [2 /*return*/, {
                                value: ret,
                                dispose: function () { }
                            }];
                }
            });
        });
    };
    return SignatureHelpAdapter;
}(Adapter));

// --- hover ------
var QuickInfoAdapter = /** @class */ (function (_super) {
    __extends(QuickInfoAdapter, _super);
    function QuickInfoAdapter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    QuickInfoAdapter.prototype.provideHover = function (model, position, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, offset, worker, info, documentation, tags, contents;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        offset = model.getOffsetAt(position);
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getQuickInfoAtPosition(resource.toString(), offset)];
                    case 2:
                        info = _a.sent();
                        if (!info || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        documentation = displayPartsToString(info.documentation);
                        tags = info.tags ? info.tags.map(function (tag) { return tagToString(tag); }).join('  \n\n') : '';
                        contents = displayPartsToString(info.displayParts);
                        return [2 /*return*/, {
                                range: this._textSpanToRange(model, info.textSpan),
                                contents: [
                                    {
                                        value: '```typescript\n' + contents + '\n```\n'
                                    },
                                    {
                                        value: documentation + (tags ? '\n\n' + tags : '')
                                    }
                                ]
                            }];
                }
            });
        });
    };
    return QuickInfoAdapter;
}(Adapter));

// --- occurrences ------
var languageFeatures_OccurrencesAdapter = /** @class */ (function (_super) {
    __extends(OccurrencesAdapter, _super);
    function OccurrencesAdapter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    OccurrencesAdapter.prototype.provideDocumentHighlights = function (model, position, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, offset, worker, entries;
            var _this = this;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        offset = model.getOffsetAt(position);
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getOccurrencesAtPosition(resource.toString(), offset)];
                    case 2:
                        entries = _a.sent();
                        if (!entries || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [2 /*return*/, entries.map(function (entry) {
                                return {
                                    range: _this._textSpanToRange(model, entry.textSpan),
                                    kind: entry.isWriteAccess
                                        ? monaco_editor_core["languages"].DocumentHighlightKind.Write
                                        : monaco_editor_core["languages"].DocumentHighlightKind.Text
                                };
                            })];
                }
            });
        });
    };
    return OccurrencesAdapter;
}(Adapter));

// --- definition ------
var languageFeatures_DefinitionAdapter = /** @class */ (function (_super) {
    __extends(DefinitionAdapter, _super);
    function DefinitionAdapter(_libFiles, worker) {
        var _this = _super.call(this, worker) || this;
        _this._libFiles = _libFiles;
        return _this;
    }
    DefinitionAdapter.prototype.provideDefinition = function (model, position, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, offset, worker, entries, result, _i, entries_1, entry, refModel;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        offset = model.getOffsetAt(position);
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getDefinitionAtPosition(resource.toString(), offset)];
                    case 2:
                        entries = _a.sent();
                        if (!entries || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        // Fetch lib files if necessary
                        return [4 /*yield*/, this._libFiles.fetchLibFilesIfNecessary(entries.map(function (entry) { return monaco_editor_core["Uri"].parse(entry.fileName); }))];
                    case 3:
                        // Fetch lib files if necessary
                        _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        result = [];
                        for (_i = 0, entries_1 = entries; _i < entries_1.length; _i++) {
                            entry = entries_1[_i];
                            refModel = this._libFiles.getOrCreateModel(entry.fileName);
                            if (refModel) {
                                result.push({
                                    uri: refModel.uri,
                                    range: this._textSpanToRange(refModel, entry.textSpan)
                                });
                            }
                        }
                        return [2 /*return*/, result];
                }
            });
        });
    };
    return DefinitionAdapter;
}(Adapter));

// --- references ------
var languageFeatures_ReferenceAdapter = /** @class */ (function (_super) {
    __extends(ReferenceAdapter, _super);
    function ReferenceAdapter(_libFiles, worker) {
        var _this = _super.call(this, worker) || this;
        _this._libFiles = _libFiles;
        return _this;
    }
    ReferenceAdapter.prototype.provideReferences = function (model, position, context, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, offset, worker, entries, result, _i, entries_2, entry, refModel;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        offset = model.getOffsetAt(position);
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getReferencesAtPosition(resource.toString(), offset)];
                    case 2:
                        entries = _a.sent();
                        if (!entries || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        // Fetch lib files if necessary
                        return [4 /*yield*/, this._libFiles.fetchLibFilesIfNecessary(entries.map(function (entry) { return monaco_editor_core["Uri"].parse(entry.fileName); }))];
                    case 3:
                        // Fetch lib files if necessary
                        _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        result = [];
                        for (_i = 0, entries_2 = entries; _i < entries_2.length; _i++) {
                            entry = entries_2[_i];
                            refModel = this._libFiles.getOrCreateModel(entry.fileName);
                            if (refModel) {
                                result.push({
                                    uri: refModel.uri,
                                    range: this._textSpanToRange(refModel, entry.textSpan)
                                });
                            }
                        }
                        return [2 /*return*/, result];
                }
            });
        });
    };
    return ReferenceAdapter;
}(Adapter));

// --- outline ------
var languageFeatures_OutlineAdapter = /** @class */ (function (_super) {
    __extends(OutlineAdapter, _super);
    function OutlineAdapter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    OutlineAdapter.prototype.provideDocumentSymbols = function (model, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, worker, items, convert, result;
            var _this = this;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getNavigationBarItems(resource.toString())];
                    case 2:
                        items = _a.sent();
                        if (!items || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        convert = function (bucket, item, containerLabel) {
                            var result = {
                                name: item.text,
                                detail: '',
                                kind: (outlineTypeTable[item.kind] || monaco_editor_core["languages"].SymbolKind.Variable),
                                range: _this._textSpanToRange(model, item.spans[0]),
                                selectionRange: _this._textSpanToRange(model, item.spans[0]),
                                tags: []
                            };
                            if (containerLabel)
                                result.containerName = containerLabel;
                            if (item.childItems && item.childItems.length > 0) {
                                for (var _i = 0, _a = item.childItems; _i < _a.length; _i++) {
                                    var child = _a[_i];
                                    convert(bucket, child, result.name);
                                }
                            }
                            bucket.push(result);
                        };
                        result = [];
                        items.forEach(function (item) { return convert(result, item); });
                        return [2 /*return*/, result];
                }
            });
        });
    };
    return OutlineAdapter;
}(Adapter));

var Kind = /** @class */ (function () {
    function Kind() {
    }
    Kind.unknown = '';
    Kind.keyword = 'keyword';
    Kind.script = 'script';
    Kind.module = 'module';
    Kind.class = 'class';
    Kind.interface = 'interface';
    Kind.type = 'type';
    Kind.enum = 'enum';
    Kind.variable = 'var';
    Kind.localVariable = 'local var';
    Kind.function = 'function';
    Kind.localFunction = 'local function';
    Kind.memberFunction = 'method';
    Kind.memberGetAccessor = 'getter';
    Kind.memberSetAccessor = 'setter';
    Kind.memberVariable = 'property';
    Kind.constructorImplementation = 'constructor';
    Kind.callSignature = 'call';
    Kind.indexSignature = 'index';
    Kind.constructSignature = 'construct';
    Kind.parameter = 'parameter';
    Kind.typeParameter = 'type parameter';
    Kind.primitiveType = 'primitive type';
    Kind.label = 'label';
    Kind.alias = 'alias';
    Kind.const = 'const';
    Kind.let = 'let';
    Kind.warning = 'warning';
    return Kind;
}());

var outlineTypeTable = Object.create(null);
outlineTypeTable[Kind.module] = monaco_editor_core["languages"].SymbolKind.Module;
outlineTypeTable[Kind.class] = monaco_editor_core["languages"].SymbolKind.Class;
outlineTypeTable[Kind.enum] = monaco_editor_core["languages"].SymbolKind.Enum;
outlineTypeTable[Kind.interface] = monaco_editor_core["languages"].SymbolKind.Interface;
outlineTypeTable[Kind.memberFunction] = monaco_editor_core["languages"].SymbolKind.Method;
outlineTypeTable[Kind.memberVariable] = monaco_editor_core["languages"].SymbolKind.Property;
outlineTypeTable[Kind.memberGetAccessor] = monaco_editor_core["languages"].SymbolKind.Property;
outlineTypeTable[Kind.memberSetAccessor] = monaco_editor_core["languages"].SymbolKind.Property;
outlineTypeTable[Kind.variable] = monaco_editor_core["languages"].SymbolKind.Variable;
outlineTypeTable[Kind.const] = monaco_editor_core["languages"].SymbolKind.Variable;
outlineTypeTable[Kind.localVariable] = monaco_editor_core["languages"].SymbolKind.Variable;
outlineTypeTable[Kind.variable] = monaco_editor_core["languages"].SymbolKind.Variable;
outlineTypeTable[Kind.function] = monaco_editor_core["languages"].SymbolKind.Function;
outlineTypeTable[Kind.localFunction] = monaco_editor_core["languages"].SymbolKind.Function;
// --- formatting ----
var FormatHelper = /** @class */ (function (_super) {
    __extends(FormatHelper, _super);
    function FormatHelper() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    FormatHelper._convertOptions = function (options) {
        return {
            ConvertTabsToSpaces: options.insertSpaces,
            TabSize: options.tabSize,
            IndentSize: options.tabSize,
            IndentStyle: IndentStyle.Smart,
            NewLineCharacter: '\n',
            InsertSpaceAfterCommaDelimiter: true,
            InsertSpaceAfterSemicolonInForStatements: true,
            InsertSpaceBeforeAndAfterBinaryOperators: true,
            InsertSpaceAfterKeywordsInControlFlowStatements: true,
            InsertSpaceAfterFunctionKeywordForAnonymousFunctions: true,
            InsertSpaceAfterOpeningAndBeforeClosingNonemptyParenthesis: false,
            InsertSpaceAfterOpeningAndBeforeClosingNonemptyBrackets: false,
            InsertSpaceAfterOpeningAndBeforeClosingTemplateStringBraces: false,
            PlaceOpenBraceOnNewLineForControlBlocks: false,
            PlaceOpenBraceOnNewLineForFunctions: false
        };
    };
    FormatHelper.prototype._convertTextChanges = function (model, change) {
        return {
            text: change.newText,
            range: this._textSpanToRange(model, change.span)
        };
    };
    return FormatHelper;
}(Adapter));

var FormatAdapter = /** @class */ (function (_super) {
    __extends(FormatAdapter, _super);
    function FormatAdapter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    FormatAdapter.prototype.provideDocumentRangeFormattingEdits = function (model, range, options, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, startOffset, endOffset, worker, edits;
            var _this = this;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        startOffset = model.getOffsetAt({
                            lineNumber: range.startLineNumber,
                            column: range.startColumn
                        });
                        endOffset = model.getOffsetAt({
                            lineNumber: range.endLineNumber,
                            column: range.endColumn
                        });
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getFormattingEditsForRange(resource.toString(), startOffset, endOffset, FormatHelper._convertOptions(options))];
                    case 2:
                        edits = _a.sent();
                        if (!edits || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [2 /*return*/, edits.map(function (edit) { return _this._convertTextChanges(model, edit); })];
                }
            });
        });
    };
    return FormatAdapter;
}(FormatHelper));

var FormatOnTypeAdapter = /** @class */ (function (_super) {
    __extends(FormatOnTypeAdapter, _super);
    function FormatOnTypeAdapter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(FormatOnTypeAdapter.prototype, "autoFormatTriggerCharacters", {
        get: function () {
            return [';', '}', '\n'];
        },
        enumerable: false,
        configurable: true
    });
    FormatOnTypeAdapter.prototype.provideOnTypeFormattingEdits = function (model, position, ch, options, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, offset, worker, edits;
            var _this = this;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        offset = model.getOffsetAt(position);
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getFormattingEditsAfterKeystroke(resource.toString(), offset, ch, FormatHelper._convertOptions(options))];
                    case 2:
                        edits = _a.sent();
                        if (!edits || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [2 /*return*/, edits.map(function (edit) { return _this._convertTextChanges(model, edit); })];
                }
            });
        });
    };
    return FormatOnTypeAdapter;
}(FormatHelper));

// --- code actions ------
var CodeActionAdaptor = /** @class */ (function (_super) {
    __extends(CodeActionAdaptor, _super);
    function CodeActionAdaptor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CodeActionAdaptor.prototype.provideCodeActions = function (model, range, context, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, start, end, formatOptions, errorCodes, worker, codeFixes, actions;
            var _this = this;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        start = model.getOffsetAt({
                            lineNumber: range.startLineNumber,
                            column: range.startColumn
                        });
                        end = model.getOffsetAt({
                            lineNumber: range.endLineNumber,
                            column: range.endColumn
                        });
                        formatOptions = FormatHelper._convertOptions(model.getOptions());
                        errorCodes = context.markers
                            .filter(function (m) { return m.code; })
                            .map(function (m) { return m.code; })
                            .map(Number);
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getCodeFixesAtPosition(resource.toString(), start, end, errorCodes, formatOptions)];
                    case 2:
                        codeFixes = _a.sent();
                        if (!codeFixes || model.isDisposed()) {
                            return [2 /*return*/, { actions: [], dispose: function () { } }];
                        }
                        actions = codeFixes
                            .filter(function (fix) {
                            // Removes any 'make a new file'-type code fix
                            return fix.changes.filter(function (change) { return change.isNewFile; }).length === 0;
                        })
                            .map(function (fix) {
                            return _this._tsCodeFixActionToMonacoCodeAction(model, context, fix);
                        });
                        return [2 /*return*/, {
                                actions: actions,
                                dispose: function () { }
                            }];
                }
            });
        });
    };
    CodeActionAdaptor.prototype._tsCodeFixActionToMonacoCodeAction = function (model, context, codeFix) {
        var edits = [];
        for (var _i = 0, _a = codeFix.changes; _i < _a.length; _i++) {
            var change = _a[_i];
            for (var _b = 0, _c = change.textChanges; _b < _c.length; _b++) {
                var textChange = _c[_b];
                edits.push({
                    resource: model.uri,
                    edit: {
                        range: this._textSpanToRange(model, textChange.span),
                        text: textChange.newText
                    }
                });
            }
        }
        var action = {
            title: codeFix.description,
            edit: { edits: edits },
            diagnostics: context.markers,
            kind: 'quickfix'
        };
        return action;
    };
    return CodeActionAdaptor;
}(FormatHelper));

// --- rename ----
var RenameAdapter = /** @class */ (function (_super) {
    __extends(RenameAdapter, _super);
    function RenameAdapter(_libFiles, worker) {
        var _this = _super.call(this, worker) || this;
        _this._libFiles = _libFiles;
        return _this;
    }
    RenameAdapter.prototype.provideRenameEdits = function (model, position, newName, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, fileName, offset, worker, renameInfo, renameLocations, edits, _i, renameLocations_1, renameLocation, model_1;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        fileName = resource.toString();
                        offset = model.getOffsetAt(position);
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, worker.getRenameInfo(fileName, offset, {
                                allowRenameOfImportPath: false
                            })];
                    case 2:
                        renameInfo = _a.sent();
                        if (renameInfo.canRename === false) {
                            // use explicit comparison so that the discriminated union gets resolved properly
                            return [2 /*return*/, {
                                    edits: [],
                                    rejectReason: renameInfo.localizedErrorMessage
                                }];
                        }
                        if (renameInfo.fileToRename !== undefined) {
                            throw new Error('Renaming files is not supported.');
                        }
                        return [4 /*yield*/, worker.findRenameLocations(fileName, offset, 
                            /*strings*/ false, 
                            /*comments*/ false, 
                            /*prefixAndSuffix*/ false)];
                    case 3:
                        renameLocations = _a.sent();
                        if (!renameLocations || model.isDisposed()) {
                            return [2 /*return*/];
                        }
                        edits = [];
                        for (_i = 0, renameLocations_1 = renameLocations; _i < renameLocations_1.length; _i++) {
                            renameLocation = renameLocations_1[_i];
                            model_1 = this._libFiles.getOrCreateModel(renameLocation.fileName);
                            if (model_1) {
                                edits.push({
                                    resource: model_1.uri,
                                    edit: {
                                        range: this._textSpanToRange(model_1, renameLocation.textSpan),
                                        text: newName
                                    }
                                });
                            }
                            else {
                                throw new Error("Unknown file " + renameLocation.fileName + ".");
                            }
                        }
                        return [2 /*return*/, { edits: edits }];
                }
            });
        });
    };
    return RenameAdapter;
}(Adapter));

// --- inlay hints ----
var languageFeatures_InlayHintsAdapter = /** @class */ (function (_super) {
    __extends(InlayHintsAdapter, _super);
    function InlayHintsAdapter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    InlayHintsAdapter.prototype.provideInlayHints = function (model, range, token) {
        return languageFeatures_awaiter(this, void 0, void 0, function () {
            var resource, fileName, start, end, worker, hints;
            var _this = this;
            return languageFeatures_generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        resource = model.uri;
                        fileName = resource.toString();
                        start = model.getOffsetAt({
                            lineNumber: range.startLineNumber,
                            column: range.startColumn
                        });
                        end = model.getOffsetAt({
                            lineNumber: range.endLineNumber,
                            column: range.endColumn
                        });
                        return [4 /*yield*/, this._worker(resource)];
                    case 1:
                        worker = _a.sent();
                        if (model.isDisposed()) {
                            return [2 /*return*/, []];
                        }
                        return [4 /*yield*/, worker.provideInlayHints(fileName, start, end)];
                    case 2:
                        hints = _a.sent();
                        return [2 /*return*/, hints.map(function (hint) {
                                return __assign(__assign({}, hint), { position: model.getPositionAt(hint.position), kind: _this._convertHintKind(hint.kind) });
                            })];
                }
            });
        });
    };
    InlayHintsAdapter.prototype._convertHintKind = function (kind) {
        switch (kind) {
            case 'Parameter':
                return monaco_editor_core["languages"].InlayHintKind.Parameter;
            case 'Type':
                return monaco_editor_core["languages"].InlayHintKind.Type;
            default:
                return monaco_editor_core["languages"].InlayHintKind.Other;
        }
    };
    return InlayHintsAdapter;
}(Adapter));


// CONCATENATED MODULE: ./node_modules/monaco-editor/esm/vs/language/typescript/tsMode.js
/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/




var javaScriptWorker;
var typeScriptWorker;
function setupTypeScript(defaults) {
    typeScriptWorker = setupMode(defaults, 'typescript');
}
function setupJavaScript(defaults) {
    javaScriptWorker = setupMode(defaults, 'javascript');
}
function getJavaScriptWorker() {
    return new Promise(function (resolve, reject) {
        if (!javaScriptWorker) {
            return reject('JavaScript not registered!');
        }
        resolve(javaScriptWorker);
    });
}
function getTypeScriptWorker() {
    return new Promise(function (resolve, reject) {
        if (!typeScriptWorker) {
            return reject('TypeScript not registered!');
        }
        resolve(typeScriptWorker);
    });
}
function setupMode(defaults, modeId) {
    var client = new workerManager_WorkerManager(modeId, defaults);
    var worker = function () {
        var uris = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            uris[_i] = arguments[_i];
        }
        return client.getLanguageServiceWorker.apply(client, uris);
    };
    var libFiles = new languageFeatures_LibFiles(worker);
    monaco_editor_core["languages"].registerCompletionItemProvider(modeId, new languageFeatures_SuggestAdapter(worker));
    monaco_editor_core["languages"].registerSignatureHelpProvider(modeId, new languageFeatures_SignatureHelpAdapter(worker));
    monaco_editor_core["languages"].registerHoverProvider(modeId, new QuickInfoAdapter(worker));
    monaco_editor_core["languages"].registerDocumentHighlightProvider(modeId, new languageFeatures_OccurrencesAdapter(worker));
    monaco_editor_core["languages"].registerDefinitionProvider(modeId, new languageFeatures_DefinitionAdapter(libFiles, worker));
    monaco_editor_core["languages"].registerReferenceProvider(modeId, new languageFeatures_ReferenceAdapter(libFiles, worker));
    monaco_editor_core["languages"].registerDocumentSymbolProvider(modeId, new languageFeatures_OutlineAdapter(worker));
    monaco_editor_core["languages"].registerDocumentRangeFormattingEditProvider(modeId, new FormatAdapter(worker));
    monaco_editor_core["languages"].registerOnTypeFormattingEditProvider(modeId, new FormatOnTypeAdapter(worker));
    monaco_editor_core["languages"].registerCodeActionProvider(modeId, new CodeActionAdaptor(worker));
    monaco_editor_core["languages"].registerRenameProvider(modeId, new RenameAdapter(libFiles, worker));
    monaco_editor_core["languages"].registerInlayHintsProvider(modeId, new languageFeatures_InlayHintsAdapter(worker));
    new languageFeatures_DiagnosticsAdapter(libFiles, defaults, modeId, worker);
    return worker;
}


/***/ })

}]);
//# sourceMappingURL=vue-peacock_trame.umd.80.js.map