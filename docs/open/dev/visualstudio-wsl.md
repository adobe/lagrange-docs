# Building Lagrange with GCC Clang in Visual Studio via WSL

## System Preparation

### Install WSL (Windows Subsystem For Linux)

Detailed instructions [here](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

In short,

1. Run ```Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux``` in PowerShell as administrator
2. Restart computer
3. Go to Microsoft Store, search for Ubuntu or other distro and install it. (tested Ubuntu 20 LTS)

### Install Unix Libraries

Start Ubuntu (found in Start menu)

**To enable Visual Studio - WSL integration**

```
sudo apt install g++ gdb make rsync zip
```

For clang, run also
```
sudo apt install clang
```

More details [here](https://devblogs.microsoft.com/cppblog/c-with-visual-studio-2019-and-windows-subsystem-for-linux-wsl/).

**If building UI, install further dependencies**

```
sudo apt-get install libglu1-mesa-dev freeglut3-dev mesa-common-dev build-essential libgtk-3-dev xorg-dev
```

### Install CMake

Visual Studio can install CMake for you automatically (a popup will appear) and it will install it into `$HOME/.vs/cmake/bin/cmake`
**However, to make sure FetchContent works with direct URL downloads, it seems you have to install CMake into Ubuntu directly via:**
```
sudo apt-get install cmake
```
**You will have to switch the CMake executable option in `CMakeSettings.json` (under Advanced) to `/usr/bin/cmake` or wherever your `apt-get` installs `cmake`**.

### Modify Visual Studio Installation

1. Go to `Add or Remove Programs -> Visual Studio Installer -> Modify`
2. Select your installation `More -> Modify`
3. Enable `Linux development with C++` and update
4. Update to latest Visual Studio version for best results.

### Install SSH Keys

1. Install keychain `sudo apt-get install keychain`
2. You can copy your windows id_rsa key to `~/.ssh/` or generate a new one
3. Add this line to .bashrc:
    ```
    eval \`keychain --agents ssh --eval id_rsa\`
    ```
4. Make sure ~/.ssh/id_rsa has chmod 0600


## Build Lagrange

### Configuration

1. Clone the repository
2. `Open Visual Studio -> File -> Open Folder -> Open Folder lagrange root folder`
3. Click on `Open the CMake Settings Editor`
4. Click on the plus icon,  select `WSL-Debug` or `WSL-Release` (this will build with GCC)
5. `Ctrl + S` or save the file to run CMake
6. In the `CmakeSettings.json` editor, you'll be able to select which lagrange modules to build
7. Save the config file again to generate the project

### Selecting Targets

Solution explorer has two views
1. `File hierarchy`
2. `CMake Targets View`

Switch to `CMake Targets View`, navigate to target you want to build, right click `Set as Startup Item` and build.

### Controlling Configuration Step

CMake will run automatically when cache is invalidated. To prevent that go to
`Tools -> Options -> CMake -> When cache is out of date` and select your preferred option.

If you want to trigger configuration step manually, in `Cmake Targets View` right click `Lagrange Project` and select `Generate Cache`

### Terminal

Go to `Debug` -> `Linux Console` to see the linux terminal.

## Bonus: Running UI Window from WSL

Note: WSL does not support GPU rendering, UI will be rendered through software driver - therefore it's quite slow. In particular, IBL generation is slow so setting `Viewer::WindowOptions::default_ibl = ""` is recommended.

1. Download and run MobaXTerm (https://mobaxterm.mobatek.net/download.html), go to X Server -> Start X Server  (other alternatives like Xming use older GLX version)
2. To test if it works, Run `export DISPLAY=:0` and then `sudo apt install mesa-utils` and run `glxgears`
3. `OpenCmakeSettings.json` in the lagrange project and add this before `configurations`:
```
"environments": [
    {
      "DISPLAY": ":0"
    }
  ],
```
4. Build and run UI examples

## More resources

- [Pure Virtual C++ 2020](https://www.youtube.com/watch?v=c1ThUFISDF4) (WSL specific session starts at 2:06:00)
- [C++ with Visual Studio 2019 and Windows Subsystem for Linux (WSL)](https://devblogs.microsoft.com/cppblog/c-with-visual-studio-2019-and-windows-subsystem-for-linux-wsl/)
- [CMake projects in Visual Studio](https://docs.microsoft.com/en-us/cpp/build/cmake-projects-in-visual-studio?view=vs-2019)
- [Launch.vs.json reference for remote projects and WSL](https://docs.microsoft.com/en-us/cpp/build/configure-cmake-debugging-sessions?view=vs-2019#launchvsjson-reference-for-remote-projects-and-wsl)
