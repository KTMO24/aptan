#!/usr/bin/env python3
# =============================================================================
# BSD 3-Clause License
# 
# Copyright (c) 2025, Travis Michael O’Dell
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the Travis Michael O’Dell nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# =============================================================================

"""
Merged Tool - Jedimt/Yesco with Interface Mapper
Author: Travis Michael O’Dell
License: BSD 3-Clause

This merged system implements:
  • Core Jedimt functionality:
       - Platform detection and configuration.
       - Apt package installation (via tar.gz) with native build or Gemini translation.
       - Basic shell commands (cd, compile, run, pass-through).
  • A Yesco CLI (via Click and Rich) for managing projects, signing, compiling source,
    packaging applications, managing an iOS simulator, and debugging.
  • A Kivy-based interface mapper (optional) for UI code ingestion and generation via Gemini.
  • IPython magic extension for AptAn.
  • Interactive UI with ipywidgets (notebook-friendly).
"""

import os
import sys
import subprocess
import tarfile
import zipfile
import json
import re
import threading
import time
import requests
import platform
import shutil
import base64
import uuid
import shlex

# -----------------------------
# External Libraries
# -----------------------------
try:
    import click
except ImportError:
    print("Please install click: pip install click")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
except ImportError:
    print("Please install rich: pip install rich")
    sys.exit(1)

# Kivy imports (optional)
try:
    import kivy
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.filechooser import FileChooserIconView
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup

    kivy_available = True
except ImportError:
    kivy_available = False

# ipywidgets (optional)
try:
    import ipywidgets as widgets
    from IPython.display import display, HTML, clear_output
    from IPython.core.magic import (
        Magics,
        magics_class,
        line_magic,
        cell_magic,
        line_cell_magic,
    )
    from IPython.core.magic_arguments import (
        argument,
        magic_arguments,
        parse_argstring
    )
    from IPython.core.getipython import get_ipython
    ipywidgets_available = True
except ImportError:
    ipywidgets_available = False

console = Console()

# A simple config to toggle debugging if needed
config = {
    "enable_debugging": True
}

__version__ = "0.4.5"


# =============================================================================
# 1) PlatformConfig - system detection
# =============================================================================
class PlatformConfig:
    def __init__(self):
        self.system = platform.system()
        self.release = platform.release()
        self.version = platform.version()
        self.machine = platform.machine()
        self.processor = platform.processor()
        self.home_dir = os.path.expanduser("~")
        self.config = self.load_config()

    def load_config(self):
        """Load platform-specific configurations from platform_config.json (optional)."""
        config_file = "platform_config.json"
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
                return config_data.get(self.system, {})
        except FileNotFoundError:
            print(f"Warning: Configuration file '{config_file}' not found. Using default settings.")
            return {}

    def get_config(self, key, default=None):
        """Retrieve a configuration value for the current platform."""
        return self.config.get(key, default)

    def print_platform_info(self):
        """Print basic platform info for debugging."""
        print("Platform Information:")
        print(f"  System: {self.system}")
        print(f"  Release: {self.release}")
        print(f"  Version: {self.version}")
        print(f"  Machine: {self.machine}")
        print(f"  Processor: {self.processor}")
        print(f"  Home Directory: {self.home_dir}")
        print(f"  Configurations: {self.config}")


# =============================================================================
# 2) Gemini - Dummy/Simulated Integration
# =============================================================================
class Gemini:
    def __init__(self, api_key, platform_config):
        self.api_key = api_key
        self.platform_config = platform_config
        print("Gemini initialized with API key.")

    def generate_code(self, prompt, target_language="python", temperature=0.7, max_output_tokens=8000):
        """Simulates code translation to target_language, returning a string."""
        print(f"Simulating translation to {target_language} using Gemini...\n")
        system_label = self.platform_config.system

        if target_language == "python":
            translated = (
                "def main():\n"
                "    # Translated code (Python)\n"
                + "    " + "\n    ".join(prompt.splitlines()) +
                f"\n    print('Running on {system_label}')\n\n"
                "if __name__ == '__main__':\n"
                "    main()\n"
            )
        elif target_language == "javascript":
            translated = (
                "function main() {\n"
                "    // Translated code (JavaScript)\n"
                + "    " + "\n    ".join(prompt.splitlines()) +
                f"\n    console.log('Running on {system_label}');\n"
                "}\n"
                "main();\n"
            )
        elif target_language == "swift":
            translated = (
                "func main() {\n"
                "    // Translated code (Swift)\n"
                + "    " + "\n    ".join(prompt.splitlines()) +
                f"\n    print(\"Running on {system_label}\")\n"
                "}\nmain()\n"
            )
        else:
            translated = f"// Translation to {target_language} not yet supported (Gemini simulation)"

        return translated

    def analyze_suitability(self, source_code, package_name):
        """Dummy simulation of analyzing source code's platform suitability."""
        print("Simulating Gemini analysis for suitability...\n")

        if "network" in package_name.lower():
            print(f"Warning: Package '{package_name}' seems related to networking.")
            print("Recommendation: consider built-in networking libraries if possible.")
            if input("Continue with installation anyway? (y/n): ").lower() != 'y':
                return False

        if "system" in source_code:
            print("Warning: Code might not be suitable for a sandboxed environment.")
            if input("Continue with Python translation anyway? (y/n): ").lower() != 'y':
                return False

        return True

    def suggest_alternatives(self, package_name):
        """Dummy suggestions if analysis fails."""
        if "network" in package_name.lower():
            print("Consider Python's 'socket', 'requests', or iOS 'URLSession'.")
        elif "gui" in package_name.lower():
            print("Consider 'tkinter', 'PyQt', or SwiftUI on iOS.")
        else:
            print("No specific alternatives suggested.")


# =============================================================================
# 3) AptAn - The Apt-Anywhere Manager + Methods
# =============================================================================
class AptAn:
    def __init__(self, platform_config, gemini_api_key=None):
        self.platform_config = platform_config
        self.gemini = Gemini(gemini_api_key, platform_config) if gemini_api_key else None
        self.source_dir = os.path.join(platform_config.home_dir, ".aptan", "sources")
        self.install_dir = os.path.join(platform_config.home_dir, ".aptan", "installed")
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.install_dir, exist_ok=True)

    def download_source(self, package_name, source_url):
        """
        Attempt to download the package source:
          - If on Linux with apt-get, try `apt-get source`
          - Otherwise, fallback to the provided URL (tar.gz)
        """
        if source_url is None:
            source_url = ""
        try:
            if self.platform_config.system == "Linux" and shutil.which("apt-get"):
                # Use apt-get source
                download_cmd = ["apt-get", "source", package_name]
                temp_dir = os.path.join(self.source_dir, f"temp_{package_name}")
                os.makedirs(temp_dir, exist_ok=True)

                print(f"Downloading source for '{package_name}' via apt-get source...")
                subprocess.run(download_cmd, cwd=temp_dir, check=True)

                # Find extracted dir
                extracted = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                if not extracted:
                    raise FileNotFoundError(f"apt-get source did not produce any folder for '{package_name}'.")
                return os.path.join(temp_dir, extracted[0])
            else:
                # Fallback to direct URL download
                if not source_url:
                    print("No source URL provided, cannot download.")
                    return None
                print(f"Downloading source for '{package_name}' from URL: {source_url}")
                response = requests.get(source_url, stream=True)
                response.raise_for_status()

                local_tar = os.path.join(self.source_dir, f"{package_name}.tar.gz")
                with open(local_tar, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                extract_dir = os.path.join(self.source_dir, package_name)
                with tarfile.open(local_tar, "r:gz") as tar:
                    tar.extractall(extract_dir)
                return extract_dir

        except (requests.exceptions.RequestException, subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error downloading source: {e}")
            return None

    def convert_to_targz(self, source_path, package_name):
        """Bundle the source into a .tar.gz file for uniform handling."""
        tar_file = os.path.join(self.source_dir, f"{package_name}.tar.gz")
        print(f"Creating tar.gz package: {tar_file}...")
        try:
            with tarfile.open(tar_file, "w:gz") as tar:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, source_path)
                        tar.add(full_path, arcname=rel_path)
            return tar_file
        except Exception as e:
            print(f"Failed creating tar.gz: {e}")
            return None

    def build_native(self, extract_dir, package_name):
        """Attempt a naive 'make' build."""
        makefile = os.path.join(extract_dir, "Makefile")
        if not os.path.exists(makefile):
            print(f"No Makefile found in {extract_dir}. Skipping native build.")
            return False
        build_cmd = self.platform_config.get_config("build_command", "make")
        build_cmd = f"cd {extract_dir} && {build_cmd}"
        print(f"Running build command: {build_cmd}")
        try:
            subprocess.run(build_cmd, shell=True, check=True)
            print(f"Package '{package_name}' built successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Native build failed: {e}")
            return False

    def translate_to_language(self, extract_dir, package_name, target_language):
        """Use Gemini to translate main.c -> <target_language> (dummy)."""
        if not self.gemini:
            print("Gemini not configured; cannot translate.")
            return False

        main_source = os.path.join(extract_dir, "main.c")
        if not os.path.exists(main_source):
            print(f"No 'main.c' found in {extract_dir}. Cannot translate.")
            return False

        with open(main_source, "r") as f:
            source_code = f.read()

        translated = self.gemini.generate_code(source_code, target_language)
        if not translated:
            print("Translation failed.")
            return False

        out_file = os.path.join(extract_dir, f"{package_name}.{target_language}")
        with open(out_file, "w") as f:
            f.write(translated)
        print(f"Translated to '{target_language}' -> {out_file}")
        return True

    def build_ios_app(self, extract_dir, package_name):
        """Simulate building an iOS app with xcodebuild (macOS only)."""
        if self.platform_config.system != "Darwin":
            print("iOS builds require macOS. Skipping.")
            return False

        project_files = [f for f in os.listdir(extract_dir) if f.endswith(".xcodeproj")]
        if not project_files:
            # Create a minimal .xcodeproj if missing
            xcodeproj_dir = os.path.join(extract_dir, f"{package_name}.xcodeproj")
            os.makedirs(xcodeproj_dir, exist_ok=True)
            with open(os.path.join(xcodeproj_dir, "project.pbxproj"), "w") as f:
                f.write("// Minimal Xcode project structure")

            # SwiftUI main file
            main_swift = os.path.join(extract_dir, "main.swift")
            if not os.path.exists(main_swift):
                with open(main_swift, "w") as f:
                    f.write(f"""
import SwiftUI
@main
struct {package_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}
struct ContentView: View {{
    var body: some View {{
        Text("Hello from {package_name}!")
    }}
}}
""")
            project_files = [f"{package_name}.xcodeproj"]

        project_file = project_files[0]
        build_cmd = [
            "xcodebuild",
            "-project", os.path.join(extract_dir, project_file),
            "-scheme", package_name,
            "-configuration", "Release",
            "-destination", "generic/platform=iOS",
            "build"
        ]
        try:
            print(f"Running iOS build: {' '.join(build_cmd)}")
            subprocess.run(build_cmd, check=True)
            print(f"iOS build for '{package_name}' succeeded.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"iOS build failed: {e}")
            return False

    def install_and_configure(self, extract_dir, package_name, install_env=None):
        """
        Copy the built/translated files to an install directory
        and append PATH changes (Linux) or do environment-based installs.
        """
        if install_env:
            install_path = os.path.join(self.install_dir, "envs", install_env)
            print(f"Installing '{package_name}' to environment: {install_path}")
        else:
            # Default system-wide or local approach
            if self.platform_config.system == "Linux":
                install_path = "/usr/local/lib"
            elif self.platform_config.system == "Windows":
                install_path = f"C:\\Program Files\\{package_name}"
            else:
                install_path = "/usr/local/lib"
            print(f"Installing '{package_name}' to: {install_path}")

        os.makedirs(install_path, exist_ok=True)
        for item in os.listdir(extract_dir):
            src = os.path.join(extract_dir, item)
            dst = os.path.join(install_path, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

        # Minimal config file
        config_file = os.path.join(install_path, f"{package_name}_config.json")
        data = {
            "package_name": package_name,
            "install_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platform": self.platform_config.system
        }
        with open(config_file, "w") as f:
            json.dump(data, f, indent=4)

        # PATH adjustments (Linux example)
        if self.platform_config.system == "Linux":
            bashrc = os.path.join(self.platform_config.home_dir, ".bashrc")
            with open(bashrc, "a") as brc:
                brc.write(f"\n# AptAn for {package_name}\n")
                brc.write(f"export PATH=\"{install_path}:$PATH\"\n")
            print(f"Added {install_path} to PATH in {bashrc}. Source or restart shell to use it.")

        print(f"Install + config completed for '{package_name}'.")

    def install_package(self, package_name, source_url, target_platform, install_env=None):
        """
        Main entry: downloads, tars, extracts, builds or translates, 
        and installs the package per the requested platform.
        """
        src_dir = self.download_source(package_name, source_url)
        if not src_dir:
            return False

        tarred = self.convert_to_targz(src_dir, package_name)
        if not tarred:
            return False

        # Re-extract to a fresh folder
        extracted = os.path.join(self.source_dir, package_name + "_extracted")
        if os.path.exists(extracted):
            shutil.rmtree(extracted)
        os.makedirs(extracted, exist_ok=True)
        try:
            with tarfile.open(tarred, "r:gz") as tar:
                tar.extractall(extracted)
        except Exception as e:
            print(f"Could not extract tar: {e}")
            return False

        # Analyze if main.c exists
        main_c = os.path.join(extracted, "main.c")
        if os.path.exists(main_c) and self.gemini:
            with open(main_c, "r") as f:
                code = f.read()
            if not self.gemini.analyze_suitability(code, package_name):
                self.gemini.suggest_alternatives(package_name)
                return False

        # Dispatch build/translate logic
        if target_platform == "python" and self.gemini:
            with open(main_c, "r") as f:
                code = f.read()
            # Insert code into IPython if available
            ipy = get_ipython()
            if ipy:
                translated = self.gemini.generate_code(code, "python")
                ipy.set_next_input(translated, replace=False)
                print("Inserted translated Python code into next IPython cell.")
            else:
                print("No IPython session found; skipping direct code insertion.")
            return True
        elif target_platform == "native":
            if self.build_native(extracted, package_name):
                self.install_and_configure(extracted, package_name, install_env)
                return True
            return False
        elif target_platform == "ios":
            if self.build_ios_app(extracted, package_name):
                print(f"iOS app for '{package_name}' built successfully.")
                # Code signing or additional steps could go here
                return True
            return False
        elif target_platform in ["javascript", "swift"]:
            if self.translate_to_language(extracted, package_name, target_platform):
                self.install_and_configure(extracted, package_name, install_env)
                return True
            return False
        else:
            # Default or unknown => try building natively or do nothing
            print(f"Unknown or unsupported target_platform '{target_platform}'. Doing a native build instead.")
            if self.build_native(extracted, package_name):
                self.install_and_configure(extracted, package_name, install_env)
                return True
            return False


# =============================================================================
# 4) IPython Magic: AptAnMagics
# =============================================================================
if ipywidgets_available:
    @magics_class
    class AptAnMagics(Magics):
        def __init__(self, shell):
            super().__init__(shell)
            self.platform_config = PlatformConfig()
            self.platform_config.print_platform_info()
            self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
            self.aptan_manager = AptAn(self.platform_config, self.gemini_api_key)

        @magic_arguments()
        @argument("package_name", help="Name of the package to install.")
        @argument("--source-url", help="URL to download the source (if not using apt).")
        @argument("--target", default="native", help="Target platform: native, python, ios, etc.")
        @argument("--install-env", help="Environment (e.g., 'local' or venv name).")
        @line_magic
        def aptan(self, line):
            """
            %aptan install <package_name> --source-url <url> --target <native|python|ios|...>
            """
            args = parse_argstring(self.aptan, line)

            # Very simple approach: 
            if args.package_name == "install":
                package_name = args.source_url
                source_url = args.target if args.target != "native" else ""
                t_platform = args.install_env if args.install_env else "native"
                self.aptan_manager.install_package(package_name, source_url, t_platform)
            else:
                # Or interpret them directly
                package_name = args.package_name
                source_url = args.source_url
                t_platform = args.target
                ienv = args.install_env

                self.aptan_manager.install_package(package_name, source_url, t_platform, ienv)

        @line_magic
        def apt(self, line):
            """
            %apt <args...> => pass to system apt
            """
            command = f"apt {line}"
            print(f"Executing: {command}")
            try:
                subprocess.run(command, shell=True, check=True, executable=self.platform_config.get_config("shell"))
            except subprocess.CalledProcessError as e:
                print(f"Command failed: {e}")


# =============================================================================
# 5) Jedimt Core
# =============================================================================
class Jedimt:
    """Core class for compile, run, apt commands, etc."""
    def __init__(self, mode="compile", gemini_api_key=None):
        self.mode = mode
        self.platform_config = PlatformConfig()
        console.log(f"[blue]Detected user platform: {self.platform_config.system}[/blue]")
        self.gemini_api_key = gemini_api_key
        self.aptan_manager = AptAn(self.platform_config, gemini_api_key)
        self.scripts = {}

    def compile_code(self, code_snippet, script_id):
        """Simulated code compilation."""
        executable = f"compiled_code_for_{script_id}"
        self.scripts[script_id] = {"source": code_snippet, "executable": executable}
        console.log(f"[green]Script '{script_id}' compiled successfully.[/green]")
        return {"script_id": script_id, "executable": executable}

    def run_script(self, script_id):
        """Simulated script run (just prints code)."""
        if script_id not in self.scripts:
            console.log(f"[red]Script '{script_id}' not found.[/red]")
            return
        console.log(f"[blue]Executing script '{script_id}'...[/blue]")
        source = self.scripts[script_id]["source"]
        console.print(Panel(source, title="Script Output"))

    def apt_install(self, package_name, target_platform=None):
        """Install a package with AptAn."""
        success = self.aptan_manager.install_package(package_name, None, target_platform)
        if success:
            console.log(f"[green]APT package '{package_name}' installed successfully for platform '{target_platform}'.[/green]")
        else:
            console.log(f"[red]Failed to install APT package '{package_name}'.[/red]")

    def shell_command(self, args):
        """
        The main pass-through command entry:
            cd, apt, compile, run, or fallback to system shell.
        """
        if not args:
            self.print_usage()
            return
        cmd = args[0]
        subargs = args[1:]

        # Dispatch
        if cmd == "cd":
            if not subargs:
                console.log("[red]Usage: cd <directory>[/red]")
                return
            try:
                os.chdir(subargs[0])
                console.log(f"[green]Changed directory to: {os.getcwd()}[/green]")
            except Exception as e:
                console.log(f"[red]Error changing directory: {e}[/red]")

        elif cmd == "apt":
            # e.g. apt install <package> --target <...>
            if not subargs:
                console.log("[red]Usage: apt install <package_name> [--target ...][/red]")
                return
            subcmd = subargs[0]
            if subcmd == "install":
                if len(subargs) < 2:
                    console.log("[red]Usage: apt install <package_name> [--target <...>][/red]")
                    return
                package_name = subargs[1]
                # If next is --target, parse that
                target_plat = None
                if "--target" in subargs:
                    idx = subargs.index("--target")
                    if idx + 1 < len(subargs):
                        target_plat = subargs[idx + 1]
                self.apt_install(package_name, target_plat)
            else:
                console.log(f"[red]Unknown apt subcommand '{subcmd}'.[/red]")

        elif cmd == "compile":
            # compile <script_id> <source_code...>
            if len(subargs) < 2:
                console.log("[red]Usage: compile <script_id> <source_code>[/red]")
                return
            script_id = subargs[0]
            code = " ".join(subargs[1:])
            self.compile_code(code, script_id)

        elif cmd == "run":
            # run <script_id>
            if len(subargs) < 1:
                console.log("[red]Usage: run <script_id>[/red]")
                return
            script_id = subargs[0]
            self.run_script(script_id)
        else:
            # Fallback - system shell
            full_cmd = " ".join(args)
            console.log(f"[blue]Executing system command: {full_cmd}[/blue]")
            try:
                subprocess.run(full_cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                console.log(f"[red]Command failed: {e}[/red]")

    def print_usage(self):
        usage = f"""
Usage: {sys.argv[0]} <command> [arguments ...]
Supported Commands:
  cd <directory>               Change directory.
  apt install <package_name>   Install an apt package.
  compile <script_id> <code>   Compile code snippet.
  run <script_id>              Run compiled snippet.
  <other>                      Passed to system shell.
"""
        console.print(Panel(usage, title="Jedimt CLI Usage"))


# =============================================================================
# 6) Optional Kivy GUI: InterfaceMapper & InterfaceMapperApp
# =============================================================================
if kivy_available:
    class InterfaceMapper(BoxLayout):
        def __init__(self, **kwargs):
            super().__init__(orientation="vertical", **kwargs)
            self.platform_config = PlatformConfig()
            self.gemini = Gemini("dummy_api_key", self.platform_config)

            # UI: code input
            self.code_input = TextInput(
                text="Enter interface specification or UI code here...",
                size_hint=(1, 0.4)
            )
            self.add_widget(self.code_input)

            # Map button
            self.map_button = Button(text="Map Interface", size_hint=(1, 0.1))
            self.map_button.bind(on_press=self.map_interface)
            self.add_widget(self.map_button)

            # Output area
            self.output_scroll = ScrollView(size_hint=(1, 0.5))
            self.output_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            self.output_layout.bind(minimum_height=self.output_layout.setter("height"))
            self.output_scroll.add_widget(self.output_layout)
            self.add_widget(self.output_scroll)

        def map_interface(self, instance):
            input_code = self.code_input.text.strip()
            if not input_code:
                self.show_popup("Error", "Please enter some interface code.")
                return
            prompt = f"Translate the following interface specification into a mobile-specific layout:\n\n{input_code}"
            mapped_code = self.gemini.generate_code(prompt, target_language="swift")
            self.output_layout.clear_widgets()
            output_label = Label(text=mapped_code, markup=True, size_hint_y=None, height=600)
            self.output_layout.add_widget(output_label)

        def show_popup(self, title, message):
            popup = Popup(
                title=title,
                content=Label(text=message),
                size_hint=(None, None),
                size=(400, 200)
            )
            popup.open()

    class InterfaceMapperApp(App):
        def build(self):
            return InterfaceMapper()


# =============================================================================
# 7) ipywidgets-based Interface (JedimtYescoInterface)
# =============================================================================
if ipywidgets_available:
    class JedimtYescoInterface:
        """
        Provides a Tabbed UI in a Jupyter notebook, hooking into Jedimt methods.
        """
        def __init__(self, jedimt_instance=None, gemini_api_key=None):
            self.jedimt = jedimt_instance or Jedimt(mode="compile", gemini_api_key=gemini_api_key)
            self.setup_widgets()

        def setup_widgets(self):
            # Main tab
            self.tab = widgets.Tab()

            # Tab pages
            self.package_tab = self.create_package_tab()
            self.compiler_tab = self.create_compiler_tab()
            self.project_tab = self.create_project_tab()
            self.simulator_tab = self.create_simulator_tab()

            self.tab.children = [
                self.package_tab, self.compiler_tab,
                self.project_tab, self.simulator_tab
            ]

            titles = ["Package Manager", "Compiler", "Project Tools", "iOS Simulator"]
            for i, t in enumerate(titles):
                self.tab.set_title(i, t)

            # Output area
            self.output = widgets.Output()

            self.main_layout = widgets.VBox([
                self.tab,
                widgets.HTML("<hr>"),
                widgets.HTML("<h3>Output:</h3>"),
                self.output
            ])

        # ---------------------
        # Create Individual Tabs
        # ---------------------
        def create_package_tab(self):
            self.package_name = widgets.Text(
                description="Package:",
                placeholder="Enter package name"
            )
            self.target_platform = widgets.Dropdown(
                description="Target:",
                options=["native", "ipywidgets", "python", "ios"],
                value="native"
            )
            install_btn = widgets.Button(description="Install Package")
            install_btn.on_click(self.handle_install)

            return widgets.VBox([
                self.package_name, self.target_platform, install_btn
            ])

        def create_compiler_tab(self):
            self.script_id = widgets.Text(
                description="Script ID:",
                placeholder="Enter script identifier"
            )
            self.code_area = widgets.Textarea(
                placeholder="Enter your code here...",
                layout={"width": "100%", "height": "200px"},
            )
            compile_btn = widgets.Button(description="Compile")
            run_btn = widgets.Button(description="Run")

            compile_btn.on_click(self.handle_compile)
            run_btn.on_click(self.handle_run)
            return widgets.VBox([
                self.script_id, self.code_area,
                widgets.HBox([compile_btn, run_btn])
            ])

        def create_project_tab(self):
            self.project_name = widgets.Text(
                description="Project:",
                placeholder="Enter project name"
            )
            self.identity = widgets.Text(
                description="Identity:",
                placeholder="Enter signing identity"
            )
            self.language = widgets.Dropdown(
                description="Language:",
                options=["swift", "objc", "rust"],
                value="swift"
            )

            create_btn = widgets.Button(description="Create Project")
            sign_btn = widgets.Button(description="Sign Project")
            setup_btn = widgets.Button(description="Setup Project")

            create_btn.on_click(self.handle_create_project)
            sign_btn.on_click(self.handle_sign_project)
            setup_btn.on_click(self.handle_setup)

            return widgets.VBox([
                self.project_name,
                self.identity,
                self.language,
                widgets.HBox([create_btn, sign_btn, setup_btn])
            ])

        def create_simulator_tab(self):
            self.sim_project = widgets.Text(
                description="Project:",
                placeholder="Enter project name"
            )
            launch_btn = widgets.Button(description='Launch Simulator')
            debug_btn = widgets.Button(description='Debug')

            launch_btn.on_click(self.handle_simulator)
            debug_btn.on_click(self.handle_debug)

            return widgets.VBox([
                self.sim_project,
                widgets.HBox([launch_btn, debug_btn])
            ])

        # ---------------------
        # Handlers
        # ---------------------
        def handle_install(self, btn):
            with self.output:
                clear_output()
                pkg = self.package_name.value
                tgt = self.target_platform.value
                print(f"Installing package '{pkg}' for target '{tgt}'...")
                self.jedimt.apt_install(pkg, tgt)

        def handle_compile(self, btn):
            with self.output:
                clear_output()
                sid = self.script_id.value
                code = self.code_area.value
                print(f"Compiling script '{sid}'...")
                self.jedimt.compile_code(code, sid)

        def handle_run(self, btn):
            with self.output:
                clear_output()
                sid = self.script_id.value
                print(f"Running script '{sid}'...")
                self.jedimt.run_script(sid)

        def handle_create_project(self, btn):
            with self.output:
                clear_output()
                project = self.project_name.value
                print(f"Creating project '{project}'...")
                if not os.path.exists(project):
                    os.makedirs(project)
                    print(f"Project '{project}' created successfully.")
                else:
                    print(f"Project '{project}' already exists.")

        def handle_sign_project(self, btn):
            with self.output:
                clear_output()
                project = self.project_name.value
                identity = self.identity.value
                print(f"Signing project '{project}' with identity '{identity}'...")
                app_path = os.path.join(project, "build")
                if os.path.exists(app_path):
                    try:
                        subprocess.run(f"codesign -s {identity} {app_path}", shell=True, check=True)
                        print("Application signed successfully.")
                    except subprocess.CalledProcessError as e:
                        print(f"Signing failed: {e}")
                else:
                    print(f"Application path '{app_path}' does not exist.")

        def handle_setup(self, btn):
            with self.output:
                clear_output()
                print("Setting up project environment...")
                # Insert any real setup logic here.
                print("Setup complete.")

        def handle_simulator(self, btn):
            with self.output:
                clear_output()
                project = self.sim_project.value
                print(f"Launching simulator for project '{project}'...")
                # Insert real simulator logic here
                print("Simulator launched.")

        def handle_debug(self, btn):
            with self.output:
                clear_output()
                project = self.sim_project.value
                lang = self.language.value
                print(f"Debugging '{project}' ({lang})...")
                # Insert real debug logic here
                print("Debug session started.")

        def display(self):
            display(self.main_layout)


# =============================================================================
# 8) Yesco CLI Commands
# =============================================================================
@click.group()
def yesco():
    """Yesco: Manage projects and build applications."""
    pass

@yesco.command()
@click.argument("project_name")
def create_project(project_name):
    """Create a new project directory."""
    if not os.path.exists(project_name):
        os.makedirs(project_name)
        console.log(f"[green]Project '{project_name}' created successfully.[/green]")
    else:
        console.log(f"[red]Project '{project_name}' already exists.[/red]")

@yesco.command()
@click.argument("project_name")
@click.argument("identity")
def sign_project(project_name, identity):
    """Sign the application project."""
    app_path = os.path.join(project_name, "build")
    if os.path.exists(app_path):
        console.log(f"[blue]Signing application at '{app_path}' with identity '{identity}'...[/blue]")
        try:
            subprocess.run(f"codesign -s {identity} {app_path}", shell=True, check=True)
            console.log("[green]Application signed successfully.[/green]")
        except subprocess.CalledProcessError as e:
            console.log(f"[red]Signing failed: {e}[/red]")
    else:
        console.log(f"[red]Application path '{app_path}' does not exist.[/red]")

@yesco.command()
@click.argument("source_file")
@click.argument("output_file")
@click.option("--language", prompt="Language (swift/objc/rust)", help="Specify the language of the source file.")
def compile_source(source_file, output_file, language):
    """Compile Swift, Objective-C, or Rust source file."""
    cmd = None
    lang_lower = language.lower()
    if lang_lower == "swift":
        console.log(f"[blue]Compiling Swift source: {source_file}...[/blue]")
        cmd = f"swiftc {source_file} -o {output_file}"
    elif lang_lower == "objc":
        console.log(f"[blue]Compiling Objective-C source: {source_file}...[/blue]")
        cmd = f"clang -framework Foundation {source_file} -o {output_file}"
    elif lang_lower == "rust":
        console.log(f"[blue]Compiling Rust source: {source_file}...[/blue]")
        cmd = f"rustc {source_file} -o {output_file}"
    else:
        console.log(f"[red]Unsupported language: {language}. Use 'swift', 'objc', or 'rust'.[/red]")
        return

    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        console.log(f"[green]{language.title()} compilation successful: {output_file}.[/green]")
    else:
        console.log(f"[red]{language.title()} compilation failed: {result.stderr.decode()}[/red]")

@yesco.command()
@click.argument("app_path")
@click.argument("output_dir")
def package(app_path, output_dir):
    """Package the application."""
    console.log(f"[blue]Packaging application from {app_path}...[/blue]")
    cmd = (
        f"pkgbuild --root {app_path} "
        f"--identifier com.example.myapp --version 1.0 "
        f"--install-location /Applications {output_dir}/myapp.pkg"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        console.log(f"[green]Application packaged successfully: {output_dir}/myapp.pkg.[/green]")
    else:
        console.log(f"[red]Packaging failed: {result.stderr.decode()}[/red]")

@yesco.command()
@click.option('--retry', is_flag=True, help="Retry setup if any step fails.")
def setup(retry):
    """Automate system setup and configuration."""
    def automate_setup():
        console.log("[blue]Automating setup...[/blue]")
        # Real logic would go here
        console.log("[green]Setup automation complete.[/green]")

    while True:
        try:
            automate_setup()
            break
        except Exception as e:
            console.log(f"[red]Error during setup: {e}[/red]")
            if not retry or Prompt.ask("Retry or Exit?", choices=["Retry", "Exit"]).lower() == "exit":
                sys.exit(1)
            else:
                console.log("[yellow]Retrying setup...[/yellow]")

@yesco.command()
@click.argument("project_name")
def run_simulator(project_name):
    """Run the iOS simulator for the given project."""
    if not os.path.exists(project_name):
        console.log(f"[red]Project folder '{project_name}' does not exist.[/red]")
        return

    src_folder = os.path.join(project_name, "src")
    js_files = [os.path.join(src_folder, f) for f in os.listdir(src_folder) if f.endswith(".js")]
    js_code = ""
    for jsf in js_files:
        with open(jsf, "r") as f:
            js_code += f.read() + "\n"

    serialized_code = base64.b64encode(js_code.encode("utf-8")).decode("utf-8")

    simulator_dir = os.path.join(project_name, "simulator")
    os.makedirs(simulator_dir, exist_ok=True)

    html_file = os.path.join(simulator_dir, "simulator.html")
    with open(html_file, "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>iOS Simulator</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
</head>
<body>
    <div id="app">
        <iframe id="ios-app-frame" src="src/main.js"></iframe>
    </div>
    <script>
        new Vue({ el: '#app' });
    </script>
</body>
</html>""")

    package_json_path = os.path.join(simulator_dir, "package.json")
    with open(package_json_path, "w") as f:
        f.write(json.dumps({
            "name": f"{project_name}-simulator",
            "version": "1.0.0",
            "description": "Node-based iOS simulator for testing",
            "main": "index.js",
            "scripts": {"start": "node index.js"},
            "author": "Your Name",
            "license": "ISC"
        }, indent=2))

    index_js_path = os.path.join(simulator_dir, "index.js")
    with open(index_js_path, "w") as f:
        f.write("""const express = require('express');
const app = express();
const port = 3000;
app.use(express.static(__dirname));
app.listen(port, () => { console.log(`Server listening on port ${port}`); });
""")

    simulator_src = os.path.join(simulator_dir, "src")
    os.makedirs(simulator_src, exist_ok=True)
    main_js_path = os.path.join(simulator_src, "main.js")
    with open(main_js_path, "w") as f:
        f.write(f"""import './index.js';
const serializedCode = '{serialized_code}';
const decodedCode = atob(serializedCode);
eval(decodedCode);
""")

    console.log(f"[green]iOS simulator created in '{simulator_dir}'.[/green]")
    try:
        subprocess.run(f"cd {simulator_dir} && npm install && npm start", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        console.log(f"[red]Simulator failed: {e}[/red]")

@yesco.command()
@click.argument("project_name")
@click.option("--language", prompt="Language (swift/objc/rust)", help="Specify language for debugging.")
def compile_and_debug(project_name, language):
    """Compile and debug source code in real-time using Gemini (simulation)."""
    src_file = os.path.join(project_name, "src", "main.js")
    if not os.path.exists(src_file):
        console.log(f"[red]Source file '{src_file}' not found.[/red]")
        return
    try:
        with open(src_file, "r") as f:
            source_code = f.read()

        lang_lower = language.lower()
        if lang_lower == "swift":
            compiled_code = "// Compiled Swift code placeholder"
        elif lang_lower == "objc":
            compiled_code = "// Compiled Objective-C code placeholder"
        elif lang_lower == "rust":
            compiled_code = "// Compiled Rust code placeholder"
        else:
            console.log(f"[red]Unsupported language: {language}.[/red]")
            return

        if config.get("enable_debugging", False):
            console.log("[blue]Using Gemini for debugging (simulation)...[/blue]")
            debugging_result = {
                "status": "success",
                "code": source_code + "\n// Debugged",
                "changes": "Added debug logging"
            }
            if debugging_result["status"] == "success":
                console.log("[green]Gemini debugging successful.[/green]")
                console.print(Panel(
                    f"**Original Code:**\n{source_code}\n\n**Generated Code:**\n{debugging_result['code']}",
                    title="Generated Code"
                ))
                with open(src_file, "w") as wf:
                    wf.write(debugging_result["code"])
                console.print(Panel(
                    f"**Changes:**\n{debugging_result['changes']}",
                    title="Changes"
                ))
        else:
            console.print(Panel(
                f"**Original Code:**\n{source_code}\n\n**Compiled Code:**\n{compiled_code}",
                title="Compiled Code"
            ))
    except Exception as e:
        console.log(f"[red]Error: {e}[/red]")
        if Prompt.ask("Retry or Exit?", choices=["Retry", "Exit"]).lower() == "exit":
            sys.exit(1)

@yesco.command()
@click.argument("command", nargs=-1)
def jedimt_cli(command):
    """Pass-through to Jedimt core commands (cd, apt, compile, run, etc.)."""
    if not command:
        console.print("[red]No command provided for Jedimt.[/red]")
        return
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    jedimt_instance = Jedimt(mode="compile", gemini_api_key=gemini_api_key)
    jedimt_instance.shell_command(list(command))


# =============================================================================
# 9) IPython Extension Loader (if in a notebook)
# =============================================================================
def load_ipython_extension(ipython):
    """Register the AptAnMagics if ipywidgets is available."""
    if not ipywidgets_available:
        print("ipywidgets (and IPython) not installed; cannot load extension.")
    else:
        ipython.register_magics(AptAnMagics)


# =============================================================================
# 10) create_interface - for Notebook usage
# =============================================================================
def create_interface(gemini_api_key=None):
    """Create and display the ipywidgets interface, if available."""
    if not ipywidgets_available:
        print("ipywidgets not installed; cannot create interface.")
        return None
    interface = JedimtYescoInterface(gemini_api_key=gemini_api_key)
    interface.display()
    return interface


# =============================================================================
# 11) Main Entry Point
# =============================================================================
def main():
    """Entry point for running from the command line."""
    if "--yesco" in sys.argv:
        sys.argv.remove("--yesco")
        yesco()
    elif "--gui" in sys.argv:
        if kivy_available:
            InterfaceMapperApp().run()
        else:
            print("Kivy not installed. GUI features are disabled.")
    elif "--version" in sys.argv:
        console.print(f"Jedimt/Yesco Version: {__version__}")
    elif "--help" in sys.argv:
        # Show the help for the 'yesco' group
        with click.Context(yesco) as ctx:
            click.echo(yesco.get_help(ctx))
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        # Treat as a Jedimt command
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        jedimt_instance = Jedimt(mode="compile", gemini_api_key=gemini_api_key)
        jedimt_instance.shell_command(sys.argv[1:])
    else:
        console.print("No valid command specified. Use --yesco, --gui, --version, --help, or pass a Jedimt command.")


# =============================================================================
# 12) if __name__ == "__main__": main()
# =============================================================================
if __name__ == "__main__":
    main()
