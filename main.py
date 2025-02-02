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
Merged Tool - Jedimt/Yesco with Interface Mapper (Enhanced Edition)
Author: Travis Michael O’Dell
License: BSD 3-Clause

Features:
  • Core Jedimt (shell commands, apt install, compile, run)
  • Yesco CLI (via Click/Rich) for build, packaging, signing, iOS simulator
  • Kivy-based interface mapper (optional)
  • IPython magic extension for AptAn
  • Enhanced ipywidgets UI with logs, progress bars, state mgmt
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

try:
    import ipywidgets as widgets
    from IPython.display import display, HTML, clear_output
    from IPython.core.magic import (
        Magics, magics_class, line_magic, cell_magic, line_cell_magic
    )
    from IPython.core.magic_arguments import (
        argument, magic_arguments, parse_argstring
    )
    from IPython.core.getipython import get_ipython
    ipywidgets_available = True
except ImportError:
    ipywidgets_available = False

console = Console()

config = {
    "enable_debugging": True
}
__version__ = "0.4.5"

# -----------------------------------------------------------------------------
# 1) PlatformConfig
# -----------------------------------------------------------------------------
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
        config_file = "platform_config.json"
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
                return data.get(self.system, {})
        except FileNotFoundError:
            print(f"Warning: '{config_file}' not found. Using defaults.")
            return {}

    def get_config(self, key, default=None):
        return self.config.get(key, default)

    def print_platform_info(self):
        print("Platform Information:")
        print(f"  System: {self.system}")
        print(f"  Release: {self.release}")
        print(f"  Version: {self.version}")
        print(f"  Machine: {self.machine}")
        print(f"  Processor: {self.processor}")
        print(f"  Home Dir: {self.home_dir}")
        print(f"  Config: {self.config}")


# -----------------------------------------------------------------------------
# 2) Gemini (Simulated)
# -----------------------------------------------------------------------------
class Gemini:
    def __init__(self, api_key, platform_config):
        self.api_key = api_key
        self.platform_config = platform_config
        print("Gemini initialized with API key.")

    def generate_code(self, prompt, target_language="python", temperature=0.7, max_output_tokens=8000):
        print(f"Simulating translation to {target_language} with Gemini...\n")
        system_label = self.platform_config.system

        if target_language == "python":
            result = (
                "def main():\n"
                "    # Translated code (Python)\n"
                + "    " + "\n    ".join(prompt.splitlines()) +
                f"\n    print('Running on {system_label}')\n\n"
                "if __name__ == '__main__':\n"
                "    main()\n"
            )
        elif target_language == "javascript":
            result = (
                "function main() {\n"
                "    // Translated code (JavaScript)\n"
                + "    " + "\n    ".join(prompt.splitlines()) +
                f"\n    console.log('Running on {system_label}');\n"
                "}\n"
                "main();\n"
            )
        elif target_language == "swift":
            result = (
                "func main() {\n"
                "    // Translated code (Swift)\n"
                + "    " + "\n    ".join(prompt.splitlines()) +
                f"\n    print(\"Running on {system_label}\")\n"
                "}\nmain()\n"
            )
        else:
            result = f"// Not supported: {target_language}"

        return result

    def analyze_suitability(self, source_code, package_name):
        print("Simulating Gemini analysis...\n")
        if "network" in package_name.lower():
            print(f"Warning: '{package_name}' is networking. Consider built-in libs.")
            if input("Continue anyway? (y/n): ").lower() != 'y':
                return False
        if "system" in source_code:
            print("Warning: potential sandbox issues.")
            if input("Continue with Python translation? (y/n): ").lower() != 'y':
                return False
        return True

    def suggest_alternatives(self, package_name):
        if "network" in package_name.lower():
            print("Try: 'requests' or 'socket' in Python, or iOS 'URLSession'.")
        else:
            print("No specific alternatives.")


# -----------------------------------------------------------------------------
# 3) AptAn
# -----------------------------------------------------------------------------
class AptAn:
    def __init__(self, platform_config, gemini_api_key=None):
        self.platform_config = platform_config
        self.gemini = Gemini(gemini_api_key, platform_config) if gemini_api_key else None
        self.source_dir = os.path.join(platform_config.home_dir, ".aptan", "sources")
        self.install_dir = os.path.join(platform_config.home_dir, ".aptan", "installed")
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.install_dir, exist_ok=True)

    def download_source(self, package_name, source_url):
        if source_url is None:
            source_url = ""
        try:
            if self.platform_config.system == "Linux" and shutil.which("apt-get"):
                cmd = ["apt-get", "source", package_name]
                temp_dir = os.path.join(self.source_dir, f"temp_{package_name}")
                os.makedirs(temp_dir, exist_ok=True)

                print(f"Downloading '{package_name}' via apt-get source...")
                subprocess.run(cmd, cwd=temp_dir, check=True)

                extracted = [
                    d for d in os.listdir(temp_dir)
                    if os.path.isdir(os.path.join(temp_dir, d))
                ]
                if not extracted:
                    raise FileNotFoundError("apt-get source produced no folder.")
                return os.path.join(temp_dir, extracted[0])
            else:
                if not source_url:
                    print("No source URL provided.")
                    return None
                print(f"Downloading '{package_name}' from URL: {source_url}")
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
            print(f"Error: {e}")
            return None

    def convert_to_targz(self, source_path, package_name):
        tar_file = os.path.join(self.source_dir, f"{package_name}.tar.gz")
        print(f"Creating tar.gz: {tar_file}")
        try:
            with tarfile.open(tar_file, "w:gz") as tar:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        fullp = os.path.join(root, file)
                        relp = os.path.relpath(fullp, source_path)
                        tar.add(fullp, arcname=relp)
            return tar_file
        except Exception as e:
            print(f"Failed: {e}")
            return None

    def build_native(self, extract_dir, package_name):
        makefile = os.path.join(extract_dir, "Makefile")
        if not os.path.exists(makefile):
            print(f"No Makefile in {extract_dir}. Skipping native build.")
            return False
        build_cmd = self.platform_config.get_config("build_command", "make")
        try:
            subprocess.run(f"cd {extract_dir} && {build_cmd}", shell=True, check=True)
            print(f"'{package_name}' built successfully (native).")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Build error: {e}")
            return False

    def translate_to_language(self, extract_dir, package_name, target_language):
        if not self.gemini:
            print("Gemini not configured.")
            return False

        main_c = os.path.join(extract_dir, "main.c")
        if not os.path.exists(main_c):
            print("No main.c to translate.")
            return False

        with open(main_c, "r") as f:
            source_code = f.read()

        translated = self.gemini.generate_code(source_code, target_language)
        if not translated:
            print("Translation failed.")
            return False

        out_file = os.path.join(extract_dir, f"{package_name}.{target_language}")
        with open(out_file, "w") as f:
            f.write(translated)

        print(f"Translated '{package_name}' -> {out_file} ({target_language})")
        return True

    def build_ios_app(self, extract_dir, package_name):
        if self.platform_config.system != "Darwin":
            print("iOS build requires macOS.")
            return False

        proj_files = [f for f in os.listdir(extract_dir) if f.endswith(".xcodeproj")]
        if not proj_files:
            # Create minimal .xcodeproj
            xcode_proj = os.path.join(extract_dir, f"{package_name}.xcodeproj")
            os.makedirs(xcode_proj, exist_ok=True)
            with open(os.path.join(xcode_proj, "project.pbxproj"), "w") as f:
                f.write("// minimal xcodeproj")

            # SwiftUI main
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
            proj_files = [f"{package_name}.xcodeproj"]

        build_cmd = [
            "xcodebuild",
            "-project", os.path.join(extract_dir, proj_files[0]),
            "-scheme", package_name,
            "-configuration", "Release",
            "-destination", "generic/platform=iOS",
            "build"
        ]
        try:
            print(f"Running iOS build: {' '.join(build_cmd)}")
            subprocess.run(build_cmd, check=True)
            print(f"iOS app '{package_name}' built.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"iOS build failed: {e}")
            return False

    def install_and_configure(self, extract_dir, package_name, install_env=None):
        if install_env:
            install_path = os.path.join(self.install_dir, "envs", install_env)
            print(f"Installing '{package_name}' to environment: {install_path}")
        else:
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

        conf_file = os.path.join(install_path, f"{package_name}_config.json")
        data = {
            "package_name": package_name,
            "install_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platform": self.platform_config.system
        }
        with open(conf_file, "w") as f:
            json.dump(data, f, indent=4)

        if self.platform_config.system == "Linux":
            bashrc = os.path.join(self.platform_config.home_dir, ".bashrc")
            with open(bashrc, "a") as brc:
                brc.write(f"\n# AptAn for {package_name}\n")
                brc.write(f"export PATH=\"{install_path}:$PATH\"\n")
            print(f"PATH updated in '{bashrc}'.")

        print(f"Installation complete for '{package_name}'.")

    def install_package(self, package_name, source_url, target_platform, install_env=None):
        src_dir = self.download_source(package_name, source_url)
        if not src_dir:
            return False

        tarred = self.convert_to_targz(src_dir, package_name)
        if not tarred:
            return False

        extracted = os.path.join(self.source_dir, package_name + "_extracted")
        if os.path.exists(extracted):
            shutil.rmtree(extracted)
        os.makedirs(extracted, exist_ok=True)

        try:
            with tarfile.open(tarred, "r:gz") as tar:
                tar.extractall(extracted)
        except Exception as e:
            print(f"Extraction error: {e}")
            return False

        main_c = os.path.join(extracted, "main.c")
        if os.path.exists(main_c) and self.gemini:
            with open(main_c, "r") as f:
                code = f.read()
            if not self.gemini.analyze_suitability(code, package_name):
                self.gemini.suggest_alternatives(package_name)
                return False

        # Decide how to build or translate
        if target_platform == "python" and self.gemini:
            with open(main_c, "r") as f:
                code = f.read()
            ipy = get_ipython()
            if ipy:
                py_code = self.gemini.generate_code(code, "python")
                ipy.set_next_input(py_code, replace=False)
                print("Inserted Python code into next cell.")
            else:
                print("No IPython session found.")
            return True
        elif target_platform == "native":
            if self.build_native(extracted, package_name):
                self.install_and_configure(extracted, package_name, install_env)
                return True
            return False
        elif target_platform == "ios":
            if self.build_ios_app(extracted, package_name):
                print(f"iOS app '{package_name}' built successfully.")
                return True
            return False
        elif target_platform in ["javascript", "swift"]:
            if self.translate_to_language(extracted, package_name, target_platform):
                self.install_and_configure(extracted, package_name, install_env)
                return True
            return False
        else:
            print(f"Unknown target '{target_platform}'. Attempting native build.")
            if self.build_native(extracted, package_name):
                self.install_and_configure(extracted, package_name, install_env)
                return True
            return False


# -----------------------------------------------------------------------------
# 4) IPython Magic (AptAnMagics)
# -----------------------------------------------------------------------------
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
        @argument("package_name", help="Package to install.")
        @argument("--source-url", help="URL if not using apt-get.")
        @argument("--target", default="native", help="Target platform: native, python, ios, etc.")
        @argument("--install-env", help="Environment (like 'local' or venv).")
        @line_magic
        def aptan(self, line):
            """
            Example:
              %aptan install <package_name> [--source-url <url>] [--target <...>] [--install-env <...>]
            """
            args = parse_argstring(self.aptan, line)
            if args.package_name == "install":
                pkg = args.source_url
                src_url = args.target if args.target != "native" else ""
                tplat = args.install_env if args.install_env else "native"
                self.aptan_manager.install_package(pkg, src_url, tplat)
            else:
                pkg = args.package_name
                src_url = args.source_url
                tplat = args.target
                ienv = args.install_env
                self.aptan_manager.install_package(pkg, src_url, tplat, ienv)

        @line_magic
        def apt(self, line):
            """
            Forward to `apt ...`
            """
            cmd = f"apt {line}"
            print(f"Executing: {cmd}")
            try:
                subprocess.run(
                    cmd,
                    shell=True,
                    check=True,
                    executable=self.platform_config.get_config("shell")
                )
            except subprocess.CalledProcessError as e:
                print(f"Error: {e}")


# -----------------------------------------------------------------------------
# 5) Jedimt Core
# -----------------------------------------------------------------------------
class Jedimt:
    def __init__(self, mode="compile", gemini_api_key=None):
        self.mode = mode
        self.platform_config = PlatformConfig()
        console.log(f"[blue]Detected platform: {self.platform_config.system}[/blue]")
        self.gemini_api_key = gemini_api_key
        self.aptan_manager = AptAn(self.platform_config, gemini_api_key)
        self.scripts = {}

    def compile_code(self, code_snippet, script_id):
        exe = f"compiled_code_for_{script_id}"
        self.scripts[script_id] = {"source": code_snippet, "executable": exe}
        console.log(f"[green]Script '{script_id}' compiled successfully.[/green]")
        return {"script_id": script_id, "executable": exe}

    def run_script(self, script_id):
        if script_id not in self.scripts:
            console.log(f"[red]No such script '{script_id}'[/red]")
            return
        console.log(f"[blue]Running script '{script_id}'...[/blue]")
        src = self.scripts[script_id]["source"]
        console.print(Panel(src, title="Script Output"))

    def apt_install(self, package_name, target_platform=None):
        success = self.aptan_manager.install_package(package_name, None, target_platform)
        if success:
            console.log(f"[green]APT package '{package_name}' installed for '{target_platform}'.[/green]")
        else:
            console.log(f"[red]Failed to install '{package_name}'.[/red]")

    def shell_command(self, args):
        if not args:
            self.print_usage()
            return
        cmd = args[0]
        subargs = args[1:]

        if cmd == "cd":
            if not subargs:
                console.log("[red]Usage: cd <dir>[/red]")
                return
            try:
                os.chdir(subargs[0])
                console.log(f"[green]Changed dir to {os.getcwd()}[/green]")
            except Exception as e:
                console.log(f"[red]Error: {e}[/red]")

        elif cmd == "apt":
            if not subargs:
                console.log("[red]Usage: apt install <pkg> [--target ...][/red]")
                return
            subcmd = subargs[0]
            if subcmd == "install":
                if len(subargs) < 2:
                    console.log("[red]Usage: apt install <pkg> [--target ...][/red]")
                    return
                pkg_name = subargs[1]
                tplat = None
                if "--target" in subargs:
                    idx = subargs.index("--target")
                    if idx+1 < len(subargs):
                        tplat = subargs[idx+1]
                self.apt_install(pkg_name, tplat)
            else:
                console.log(f"[red]Unknown subcmd: apt {subcmd}[/red]")

        elif cmd == "compile":
            if len(subargs) < 2:
                console.log("[red]Usage: compile <script_id> <source>[/red]")
                return
            sid = subargs[0]
            code = " ".join(subargs[1:])
            self.compile_code(code, sid)

        elif cmd == "run":
            if len(subargs) < 1:
                console.log("[red]Usage: run <script_id>[/red]")
                return
            sid = subargs[0]
            self.run_script(sid)

        else:
            # Fallback to system shell
            full_cmd = " ".join(args)
            console.log(f"[blue]System command: {full_cmd}[/blue]")
            try:
                subprocess.run(full_cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                console.log(f"[red]Command error: {e}[/red]")

    def print_usage(self):
        console.print(Panel(
            f"Usage: {sys.argv[0]} <command> [args]\n"
            "Commands:\n"
            "  cd <directory>\n"
            "  apt install <package> [--target ...]\n"
            "  compile <script_id> <code>\n"
            "  run <script_id>\n"
            "Else pass to system shell.",
            title="Jedimt CLI Usage"
        ))


# -----------------------------------------------------------------------------
# 6) Optional Kivy GUI
# -----------------------------------------------------------------------------
if kivy_available:
    class InterfaceMapper(BoxLayout):
        def __init__(self, **kwargs):
            super().__init__(orientation="vertical", **kwargs)
            self.platform_config = PlatformConfig()
            self.gemini = Gemini("dummy_api_key", self.platform_config)
            self.code_input = TextInput(
                text="Enter interface specification here...",
                size_hint=(1, 0.4)
            )
            self.add_widget(self.code_input)
            self.map_button = Button(text="Map Interface", size_hint=(1, 0.1))
            self.map_button.bind(on_press=self.map_interface)
            self.add_widget(self.map_button)

            self.output_scroll = ScrollView(size_hint=(1, 0.5))
            self.output_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            self.output_layout.bind(minimum_height=self.output_layout.setter("height"))
            self.output_scroll.add_widget(self.output_layout)
            self.add_widget(self.output_scroll)

        def map_interface(self, instance):
            text = self.code_input.text.strip()
            if not text:
                self.show_popup("Error", "No interface code.")
                return
            prompt = "Translate to a mobile layout:\n\n" + text
            mapped = self.gemini.generate_code(prompt, "swift")
            self.output_layout.clear_widgets()
            lbl = Label(text=mapped, markup=True, size_hint_y=None, height=600)
            self.output_layout.add_widget(lbl)

        def show_popup(self, title, msg):
            popup = Popup(
                title=title,
                content=Label(text=msg),
                size_hint=(None, None),
                size=(400,200)
            )
            popup.open()

    class InterfaceMapperApp(App):
        def build(self):
            return InterfaceMapper()


# -----------------------------------------------------------------------------
# 7) Enhanced ipywidgets-based Interface (JedimtYescoInterface)
# -----------------------------------------------------------------------------
if ipywidgets_available:
    class JedimtYescoInterface:
        """
        Enhanced ipywidgets interface with improved output handling, logging,
        state management, and UX improvements.
        """
        def __init__(self, jedimt_instance=None, gemini_api_key=None):
            self.jedimt = jedimt_instance or Jedimt(mode="compile", gemini_api_key=gemini_api_key)
            self.state = {
                'current_project': None,
                'last_compile_result': None,
                'compile_history': [],
                'package_history': [],
                'logs': []
            }
            self.setup_logging()
            self.setup_widgets()

        # --------------------------
        # Logging + Output
        # --------------------------
        def setup_logging(self):
            self.log_output = widgets.Output()

        def log(self, message, level="INFO"):
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = f"[{timestamp}] {level}: {message}"
            self.state['logs'].append(entry)
            with self.log_output:
                if level == "ERROR":
                    print(f"\033[91m{entry}\033[0m")
                elif level == "WARNING":
                    print(f"\033[93m{entry}\033[0m")
                else:
                    print(entry)

        # --------------------------
        # Main Widgets + Layout
        # --------------------------
        def setup_widgets(self):
            self.status_bar = widgets.HTML(
                value='<div style="padding: 5px; background-color: #f0f0f0;">Ready</div>'
            )

            self.tab = widgets.Tab()
            self.progress = widgets.FloatProgress(
                value=0, min=0, max=100, description='Progress:',
                style={'bar_color': '#1a75ff'},
                layout={'width': '50%'}
            )

            # Tab pages
            self.package_tab = self.create_package_tab()
            self.compiler_tab = self.create_compiler_tab()
            self.project_tab = self.create_project_tab()
            self.simulator_tab = self.create_simulator_tab()
            self.logs_tab = self.create_logs_tab()

            self.tab.children = [
                self.package_tab,
                self.compiler_tab,
                self.project_tab,
                self.simulator_tab,
                self.logs_tab
            ]
            titles = ["Package Manager", "Compiler", "Project Tools", "iOS Simulator", "Logs"]
            for i, t in enumerate(titles):
                self.tab.set_title(i, t)

            self.output = widgets.Output()

            clear_btn = widgets.Button(
                description='Clear Output',
                button_style='warning',
                layout={'width': 'auto'}
            )
            clear_btn.on_click(self.clear_output)

            self.main_layout = widgets.VBox([
                self.status_bar,
                self.tab,
                widgets.HBox([self.progress, clear_btn]),
                widgets.HTML("<h3>Output:</h3>"),
                self.output,
                widgets.HTML("<h3>Logs:</h3>"),
                self.log_output
            ], layout=widgets.Layout(padding='10px'))

        # --------------------------
        # Tabs
        # --------------------------
        def create_package_tab(self):
            self.package_name = widgets.Text(
                description="Package:", placeholder="Enter package name",
                layout={'width': '50%'}
            )
            self.target_platform = widgets.Dropdown(
                description="Target:",
                options=["native", "ipywidgets", "python", "ios"],
                value="native",
                layout={'width': '50%'}
            )
            self.package_history_dropdown = widgets.Dropdown(
                description="History:", options=[], layout={'width': '50%'}
            )
            install_btn = widgets.Button(
                description="Install Package", button_style='info', icon='check'
            )
            install_btn.on_click(self.handle_install)

            return widgets.VBox([
                widgets.HBox([self.package_name, self.target_platform]),
                self.package_history_dropdown,
                install_btn
            ], layout=widgets.Layout(padding='10px'))

        def create_compiler_tab(self):
            self.script_id = widgets.Text(
                description="Script ID:", placeholder="Enter script identifier",
                layout={'width': '50%'}
            )
            self.code_area = widgets.Textarea(
                placeholder="Enter your code here...",
                layout={'width': '100%', 'height': '300px'},
            )
            self.optimization_level = widgets.Dropdown(
                description="Optimization:",
                options=['O0', 'O1', 'O2', 'O3'],
                value='O2',
                layout={'width': '30%'}
            )
            compile_btn = widgets.Button(description="Compile", button_style='primary', icon='cog')
            run_btn = widgets.Button(description="Run", button_style='success', icon='play')

            compile_btn.on_click(self.handle_compile)
            run_btn.on_click(self.handle_run)

            return widgets.VBox([
                self.script_id,
                self.optimization_level,
                self.code_area,
                widgets.HBox([compile_btn, run_btn])
            ], layout=widgets.Layout(padding='10px'))

        def create_project_tab(self):
            self.project_name = widgets.Text(
                description="Project:",
                placeholder="Enter project name",
                layout={'width': '50%'}
            )
            self.identity = widgets.Text(
                description="Identity:",
                placeholder="Enter signing identity",
                layout={'width': '50%'}
            )
            self.language = widgets.Dropdown(
                description="Language:",
                options=["swift", "objc", "rust"],
                value="swift",
                layout={'width': '30%'}
            )

            # Accordion for extra settings
            self.settings_accordion = widgets.Accordion([
                widgets.VBox([
                    widgets.Checkbox(description='Enable debugging', value=True),
                    widgets.Checkbox(description='Generate documentation', value=True),
                    widgets.Text(description='Version:', value='1.0.0')
                ])
            ])
            self.settings_accordion.set_title(0, 'Project Settings')

            create_btn = widgets.Button(description="Create Project", button_style='primary', icon='plus')
            sign_btn = widgets.Button(description="Sign Project", button_style='warning', icon='pencil')
            setup_btn = widgets.Button(description="Setup Project", button_style='info', icon='gear')

            create_btn.on_click(self.handle_create_project)
            sign_btn.on_click(self.handle_sign_project)
            setup_btn.on_click(self.handle_setup)

            return widgets.VBox([
                widgets.HBox([self.project_name, self.identity]),
                self.language,
                self.settings_accordion,
                widgets.HBox([create_btn, sign_btn, setup_btn])
            ], layout=widgets.Layout(padding='10px'))

        def create_simulator_tab(self):
            self.sim_project = widgets.Text(
                description="Project:", placeholder="Enter project name",
                layout={'width': '50%'}
            )
            self.device_selector = widgets.Dropdown(
                description="Device:",
                options=['iPhone 14 Pro', 'iPhone 14', 'iPhone SE', 'iPad Pro 12.9"', 'iPad Air'],
                value='iPhone 14 Pro',
                layout={'width': '50%'}
            )
            self.orientation = widgets.ToggleButtons(
                options=['Portrait', 'Landscape'],
                value='Portrait',
                layout={'width': 'auto'}
            )
            launch_btn = widgets.Button(description='Launch Simulator', button_style='success', icon='play')
            debug_btn = widgets.Button(description='Debug', button_style='warning', icon='bug')

            launch_btn.on_click(self.handle_simulator)
            debug_btn.on_click(self.handle_debug)

            return widgets.VBox([
                self.sim_project,
                widgets.HBox([self.device_selector, self.orientation]),
                widgets.HBox([launch_btn, debug_btn])
            ], layout=widgets.Layout(padding='10px'))

        def create_logs_tab(self):
            self.log_filter = widgets.Dropdown(
                description="Level:",
                options=['ALL', 'INFO', 'WARNING', 'ERROR'],
                value='ALL',
                layout={'width': '30%'}
            )
            self.log_filter.observe(self.filter_logs, names='value')
            clear_logs_btn = widgets.Button(description='Clear Logs', button_style='danger', icon='trash')
            clear_logs_btn.on_click(self.clear_logs)
            export_logs_btn = widgets.Button(description='Export Logs', button_style='info', icon='download')
            export_logs_btn.on_click(self.export_logs)

            return widgets.VBox([
                widgets.HBox([self.log_filter, clear_logs_btn, export_logs_btn]),
                self.log_output
            ], layout=widgets.Layout(padding='10px'))

        # --------------------------
        # Helper Methods
        # --------------------------
        def update_status(self, msg, color='black'):
            self.status_bar.value = f'<div style="padding: 5px; background-color: #f0f0f0; color: {color};">{msg}</div>'

        def update_progress(self, value):
            self.progress.value = value

        def clear_output(self, _btn=None):
            with self.output:
                clear_output()

        def clear_logs(self, _btn=None):
            self.state['logs'] = []
            with self.log_output:
                clear_output()

        def export_logs(self, _btn=None):
            stamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"jedimt_logs_{stamp}.txt"
            with open(filename, 'w') as f:
                f.write('\n'.join(self.state['logs']))
            self.log(f"Logs exported to {filename}", "INFO")

        def filter_logs(self, change):
            level = change['new']
            with self.log_output:
                clear_output()
                for log_line in self.state['logs']:
                    if level == 'ALL' or f"{level}:" in log_line:
                        print(log_line)

        # --------------------------
        # Event Handlers
        # --------------------------
        def handle_install(self, _btn):
            self.update_status("Installing package...", "blue")
            self.update_progress(0)
            with self.output:
                clear_output()
                try:
                    pkg = self.package_name.value
                    tgt = self.target_platform.value
                    if not pkg:
                        raise ValueError("Package name is required")
                    self.log(f"Starting installation of '{pkg}' for '{tgt}'")
                    self.update_progress(30)

                    if pkg not in self.state['package_history']:
                        self.state['package_history'].append(pkg)
                        self.package_history_dropdown.options = self.state['package_history']

                    self.update_progress(60)
                    self.jedimt.apt_install(pkg, tgt)
                    self.update_progress(100)

                    self.log(f"Installed '{pkg}' successfully")
                    self.update_status("Installation complete", "green")
                except Exception as e:
                    self.log(f"Installation failed: {e}", "ERROR")
                    self.update_status("Installation failed", "red")
                finally:
                    self.update_progress(0)

        def handle_compile(self, _btn):
            self.update_status("Compiling script...", "blue")
            self.update_progress(0)
            with self.output:
                clear_output()
                try:
                    sid = self.script_id.value
                    code = self.code_area.value
                    if not sid or not code.strip():
                        raise ValueError("Script ID and code required.")
                    self.log(f"Compiling '{sid}' with optimization {self.optimization_level.value}")
                    self.update_progress(50)
                    result = self.jedimt.compile_code(code, sid)
                    self.state['last_compile_result'] = result
                    self.state['compile_history'].append(result)
                    print(f"Script '{sid}' compiled.")
                    self.log(f"Compile success: {result}")
                    self.update_status("Compilation complete", "green")
                except Exception as e:
                    self.log(f"Compile error: {e}", "ERROR")
                    self.update_status("Compile failed", "red")
                finally:
                    self.update_progress(0)

        def handle_run(self, _btn):
            self.update_status("Running script...", "blue")
            self.update_progress(0)
            with self.output:
                clear_output()
                try:
                    sid = self.script_id.value
                    if not sid:
                        raise ValueError("Script ID required to run.")
                    self.update_progress(50)
                    self.jedimt.run_script(sid)
                    self.update_progress(100)
                    self.update_status("Script run complete", "green")
                except Exception as e:
                    self.log(f"Run error: {e}", "ERROR")
                    self.update_status("Run failed", "red")
                finally:
                    self.update_progress(0)

        def handle_create_project(self, _btn):
            self.update_status("Creating project...", "blue")
            self.update_progress(0)
            with self.output:
                clear_output()
                try:
                    proj = self.project_name.value
                    if not proj:
                        raise ValueError("Project name is required.")
                    self.log(f"Creating project '{proj}'")
                    self.update_progress(40)
                    if not os.path.exists(proj):
                        os.makedirs(proj)
                        print(f"Project '{proj}' created.")
                    else:
                        print(f"Project '{proj}' already exists.")
                    self.update_progress(100)
                    self.update_status("Project creation complete", "green")
                except Exception as e:
                    self.log(f"Create project error: {e}", "ERROR")
                    self.update_status("Project creation failed", "red")
                finally:
                    self.update_progress(0)

        def handle_sign_project(self, _btn):
            self.update_status("Signing project...", "blue")
            self.update_progress(0)
            with self.output:
                clear_output()
                try:
                    proj = self.project_name.value
                    ident = self.identity.value
                    if not proj or not ident:
                        raise ValueError("Project name and identity required.")
                    app_path = os.path.join(proj, "build")
                    self.update_progress(40)
                    if os.path.exists(app_path):
                        cmd = f"codesign -s {ident} {app_path}"
                        subprocess.run(cmd, shell=True, check=True)
                        print("App signed successfully.")
                        self.log(f"Signed '{proj}' with identity '{ident}'")
                        self.update_progress(100)
                        self.update_status("Signing complete", "green")
                    else:
                        raise FileNotFoundError(f"Path '{app_path}' doesn't exist.")
                except Exception as e:
                    self.log(f"Sign error: {e}", "ERROR")
                    self.update_status("Signing failed", "red")
                finally:
                    self.update_progress(0)

        def handle_setup(self, _btn):
            self.update_status("Setting up project...", "blue")
            self.update_progress(0)
            with self.output:
                clear_output()
                try:
                    self.log("Performing project setup tasks.")
                    time.sleep(1)  # simulate
                    print("Setup complete.")
                    self.update_progress(100)
                    self.update_status("Setup complete", "green")
                except Exception as e:
                    self.log(f"Setup error: {e}", "ERROR")
                    self.update_status("Setup failed", "red")
                finally:
                    self.update_progress(0)

        def handle_simulator(self, _btn):
            self.update_status("Launching simulator...", "blue")
            self.update_progress(0)
            with self.output:
                clear_output()
                try:
                    proj = self.sim_project.value
                    dev = self.device_selector.value
                    orient = self.orientation.value
                    if not proj:
                        raise ValueError("Project name required.")
                    self.log(f"Launch simulator for '{proj}' on device '{dev}' ({orient})")
                    time.sleep(1)  # simulate
                    print(f"Simulator launched for '{proj}' with device '{dev}'. Orientation: {orient}")
                    self.update_progress(100)
                    self.update_status("Simulator running", "green")
                except Exception as e:
                    self.log(f"Simulator error: {e}", "ERROR")
                    self.update_status("Simulator failed", "red")
                finally:
                    self.update_progress(0)

        def handle_debug(self, _btn):
            self.update_status("Debugging...", "blue")
            self.update_progress(0)
            with self.output:
                clear_output()
                try:
                    proj = self.sim_project.value
                    lang = self.language.value
                    if not proj:
                        raise ValueError("Project name required.")
                    self.log(f"Debugging '{proj}' in {lang}")
                    time.sleep(1)  # simulate
                    print(f"Debug session started for '{proj}' ({lang}).")
                    self.update_progress(100)
                    self.update_status("Debug session active", "green")
                except Exception as e:
                    self.log(f"Debug error: {e}", "ERROR")
                    self.update_status("Debug failed", "red")
                finally:
                    self.update_progress(0)

        # --------------------------
        # Display
        # --------------------------
        def display(self):
            display(self.main_layout)


# -----------------------------------------------------------------------------
# 8) Yesco CLI
# -----------------------------------------------------------------------------
@click.group()
def yesco():
    """Yesco: Manage projects and build applications."""
    pass

@yesco.command()
@click.argument("project_name")
def create_project(project_name):
    if not os.path.exists(project_name):
        os.makedirs(project_name)
        console.log(f"[green]Project '{project_name}' created.[/green]")
    else:
        console.log(f"[red]Project '{project_name}' already exists.[/red]")

@yesco.command()
@click.argument("project_name")
@click.argument("identity")
def sign_project(project_name, identity):
    app_path = os.path.join(project_name, "build")
    if os.path.exists(app_path):
        console.log(f"[blue]Signing '{app_path}' with identity '{identity}'...[/blue]")
        try:
            subprocess.run(f"codesign -s {identity} {app_path}", shell=True, check=True)
            console.log("[green]App signed successfully.[/green]")
        except subprocess.CalledProcessError as e:
            console.log(f"[red]Signing failed: {e}[/red]")
    else:
        console.log(f"[red]Path '{app_path}' does not exist.[/red]")

@yesco.command()
@click.argument("source_file")
@click.argument("output_file")
@click.option("--language", prompt="Language (swift/objc/rust)", help="Language of the source file.")
def compile_source(source_file, output_file, language):
    lang_lower = language.lower()
    if lang_lower == "swift":
        cmd = f"swiftc {source_file} -o {output_file}"
    elif lang_lower == "objc":
        cmd = f"clang -framework Foundation {source_file} -o {output_file}"
    elif lang_lower == "rust":
        cmd = f"rustc {source_file} -o {output_file}"
    else:
        console.log(f"[red]Unsupported language: {language}.[/red]")
        return

    console.log(f"[blue]Compiling {language} source: {source_file}[/blue]")
    res = subprocess.run(cmd, shell=True, capture_output=True)
    if res.returncode == 0:
        console.log(f"[green]{language.title()} compilation successful: {output_file}.[/green]")
    else:
        console.log(f"[red]{language.title()} failed: {res.stderr.decode()}[/red]")

@yesco.command()
@click.argument("app_path")
@click.argument("output_dir")
def package(app_path, output_dir):
    console.log(f"[blue]Packaging '{app_path}'...[/blue]")
    cmd = (
        f"pkgbuild --root {app_path} "
        f"--identifier com.example.myapp --version 1.0 "
        f"--install-location /Applications {output_dir}/myapp.pkg"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        console.log(f"[green]Packaged -> {output_dir}/myapp.pkg[/green]")
    else:
        console.log(f"[red]Packaging failed: {result.stderr.decode()}[/red]")

@yesco.command()
@click.option('--retry', is_flag=True, help="Retry setup if any step fails.")
def setup(retry):
    def automate_setup():
        console.log("[blue]Automating setup...[/blue]")
        # Real logic
        console.log("[green]Setup complete.[/green]")

    while True:
        try:
            automate_setup()
            break
        except Exception as e:
            console.log(f"[red]Error: {e}[/red]")
            if not retry or Prompt.ask("Retry or Exit?", choices=["Retry", "Exit"]).lower() == "exit":
                sys.exit(1)
            else:
                console.log("[yellow]Retrying setup...[/yellow]")

@yesco.command()
@click.argument("project_name")
def run_simulator(project_name):
    if not os.path.exists(project_name):
        console.log(f"[red]Folder '{project_name}' not found.[/red]")
        return
    src_folder = os.path.join(project_name, "src")
    if not os.path.isdir(src_folder):
        console.log(f"[red]No 'src' folder in '{project_name}'.[/red]")
        return

    js_files = [os.path.join(src_folder, f) for f in os.listdir(src_folder) if f.endswith(".js")]
    js_code = ""
    for jf in js_files:
        with open(jf, "r") as f:
            js_code += f.read() + "\n"
    serialized_code = base64.b64encode(js_code.encode("utf-8")).decode()

    sim_dir = os.path.join(project_name, "simulator")
    os.makedirs(sim_dir, exist_ok=True)

    html_file = os.path.join(sim_dir, "simulator.html")
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
  <script> new Vue({ el: '#app' }); </script>
</body>
</html>""")

    pkgjson = {
        "name": f"{project_name}-simulator",
        "version": "1.0.0",
        "description": "Node-based iOS simulator for testing",
        "main": "index.js",
        "scripts": {"start": "node index.js"},
        "author": "Your Name",
        "license": "ISC"
    }
    with open(os.path.join(sim_dir, "package.json"), "w") as f:
        f.write(json.dumps(pkgjson, indent=2))

    with open(os.path.join(sim_dir, "index.js"), "w") as f:
        f.write("""const express = require('express');
const app = express();
const port = 3000;
app.use(express.static(__dirname));
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
""")

    sim_src = os.path.join(sim_dir, "src")
    os.makedirs(sim_src, exist_ok=True)

    with open(os.path.join(sim_src, "main.js"), "w") as f:
        f.write(f"""import './index.js';
const serializedCode = '{serialized_code}';
const decodedCode = atob(serializedCode);
eval(decodedCode);
""")

    console.log(f"[green]Simulator setup in '{sim_dir}'.[/green]")
    try:
        subprocess.run(f"cd {sim_dir} && npm install && npm start", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        console.log(f"[red]Simulator failed: {e}[/red]")

@yesco.command()
@click.argument("project_name")
@click.option("--language", prompt="Language (swift/objc/rust)", help="Specify language for debugging.")
def compile_and_debug(project_name, language):
    src_file = os.path.join(project_name, "src", "main.js")
    if not os.path.exists(src_file):
        console.log(f"[red]No source '{src_file}' found.[/red]")
        return
    try:
        with open(src_file, "r") as f:
            source_code = f.read()

        lang_lower = language.lower()
        if lang_lower == "swift":
            compiled = "// Swift code placeholder"
        elif lang_lower == "objc":
            compiled = "// ObjC code placeholder"
        elif lang_lower == "rust":
            compiled = "// Rust code placeholder"
        else:
            console.log(f"[red]Unsupported language '{language}'.[/red]")
            return

        if config.get("enable_debugging", False):
            console.log("[blue]Using Gemini debugging (simulation)...[/blue]")
            dbg_result = {
                "status": "success",
                "code": source_code + "\n// Debugged",
                "changes": "Added debug logging"
            }
            if dbg_result["status"] == "success":
                console.log("[green]Debug success.[/green]")
                console.print(Panel(f"**Original:**\n{source_code}\n\n**Debugged:**\n{dbg_result['code']}",
                                    title="Generated Code"))
                with open(src_file, "w") as wf:
                    wf.write(dbg_result["code"])
                console.print(Panel(f"**Changes:**\n{dbg_result['changes']}",
                                    title="Changes"))
        else:
            console.print(Panel(f"**Original:**\n{source_code}\n\n**Compiled:**\n{compiled}",
                                title="Compiled Code"))
    except Exception as e:
        console.log(f"[red]Error: {e}[/red]")
        if Prompt.ask("Retry or Exit?", choices=["Retry", "Exit"]).lower() == "exit":
            sys.exit(1)

@yesco.command()
@click.argument("command", nargs=-1)
def jedimt_cli(command):
    if not command:
        console.print("[red]No command for Jedimt.[/red]")
        return
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    jinst = Jedimt(mode="compile", gemini_api_key=gemini_api_key)
    jinst.shell_command(list(command))


# -----------------------------------------------------------------------------
# 9) IPython Extension Loader
# -----------------------------------------------------------------------------
def load_ipython_extension(ipython):
    if not ipywidgets_available:
        print("ipywidgets not installed.")
    else:
        ipython.register_magics(AptAnMagics)


# -----------------------------------------------------------------------------
# 10) create_interface
# -----------------------------------------------------------------------------
def create_interface(gemini_api_key=None):
    if not ipywidgets_available:
        print("ipywidgets not installed; cannot create interface.")
        return None
    interface = JedimtYescoInterface(gemini_api_key=gemini_api_key)
    interface.display()
    return interface


# -----------------------------------------------------------------------------
# 11) main()
# -----------------------------------------------------------------------------
def main():
    if "--yesco" in sys.argv:
        sys.argv.remove("--yesco")
        yesco()
    elif "--gui" in sys.argv:
        if kivy_available:
            InterfaceMapperApp().run()
        else:
            print("Kivy not installed. GUI disabled.")
    elif "--version" in sys.argv:
        console.print(f"Jedimt/Yesco Version: {__version__}")
    elif "--help" in sys.argv:
        with click.Context(yesco) as ctx:
            click.echo(yesco.get_help(ctx))
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        jinst = Jedimt(mode="compile", gemini_api_key=gemini_api_key)
        jinst.shell_command(sys.argv[1:])
    else:
        console.print("No valid command. Use --yesco, --gui, --version, --help, or Jedimt commands.")


if __name__ == "__main__":
    main()
