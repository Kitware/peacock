# Desktop bundle for Windows

This relies on [pyinstaller](https://pyinstaller.org/en/stable/) to bundle your trame application into a standalone desktop application.

## Building the bundle

First, run `pip install -r requirements.txt`. This includes `pyinstaller` and `pywebview`, which is required for trame desktop applications.

Next, take a look at the `run.py` file. This should be just a regular python script that starts your trame desktop application. It can be tested via `python run.py`. Due to multiprocessing in some applications, `multiprocessing.freeze_support()` may be required to avoid an infinite recursion of running the script.

Once `python run.py` seems to be working properly, take a look at `create_exe.bat`. This is the pyinstaller command that we will use. Explanations for each option are provided:

1. `--hidden-import vtkmodules.all`: pyinstaller tries to find every dependency, but sometimes it is not able to. You can add additional python dependencies via the `--hidden-import` option, which may be specified multiple times.

For VTK applications, we can include all VTK modules, or to reduce the final binary size, only include the VTK modules that are actually used. The VTK hooks in pyinstaller should be updated in the future so that this is not necessary; see [pyinstaller/pyinstaller-hooks-contrib#327](https://github.com/pyinstaller/pyinstaller-hooks-contrib/issues/327) for details.

2. `--collect-data pywebvue`: normally, pyinstaller will only install python dependencies. For trame, however, we need some javascript files too. Adding this command will get pyinstaller to install the `pywebvue` javascript files as well.

3. `--onefile`: create a single executable for the output. `pyinstaller` by default creates a folder that contains the executable. The single executable is stand-alone and easy to move between computers. The only downside is that it takes a little longer to start and stop compared to the folder executable, because it must unpack itself before starting.

Note: if you are debugging your `pyinstaller` application, consider removing this option. It is much easier to see whether files/folders ended up in the right place in the folder executable mode.

4. `--windowed`: on Mac and Windows, this prevents the terminal/command prompt from being opened when the application is started.

5. `--icon peacock-trame.ico`: the icon file to use for the application.

After running `pyinstaller`, the standalone application may be found inside the `dist` directory that is created.
