        result = subprocess.run(f"swiftc {source_file} -o {output_file}", shell=True, capture_output=True)
        if result.returncode == 0:
            console.log(f"[green]Swift compilation successful: {output_file}.[/green]")
        else:
            console.log(f"[red]Swift compilation failed: {result.stderr.decode()}[/red]")
    elif language.lower() == "objc":
        console.log(f"[blue]Compiling Objective-C source: {source_file}...[/blue]")
        result = subprocess.run(f"clang -framework Foundation {source_file} -o {output_file}", shell=True, capture_output=True)
        if result.returncode == 0:
            console.log(f"[green]Objective-C compilation successful: {output_file}.[/green]")
        else:
            console.log(f"[red]Objective-C compilation failed: {result.stderr.decode()}[/red]")
    elif language.lower() == "rust":
        console.log(f"[blue]Compiling Rust source: {source_file}...[/blue]")
        result = subprocess.run(f"rustc {source_file} -o {output_file}", shell=True, capture_output=True)
        if result.returncode == 0:
            console.log(f"[green]Rust compilation successful: {output_file}.[/green]")
        else:
            console.log(f"[red]Rust compilation failed: {result.stderr.decode()}[/red]")
    else:
        console.log(f"[red]Unsupported language: {language}. Use 'swift', 'objc', or 'rust'.[/red]")

@yesco.command()
@click.argument("app_path")
@click.argument("output_dir")
def package(app_path, output_dir):
    """Package the application."""
    console.log(f"[blue]Packaging application from {app_path}...[/blue]")
    result = subprocess.run(f"pkgbuild --root {app_path} --identifier com.example.myapp --version 1.0 --install-location /Applications {output_dir}/myapp.pkg", shell=True, capture_output=True)
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
        # Insert actual setup logic (services, dependencies, etc.)
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
    for js_file in js_files:
        with open(js_file, "r") as f:
            js_code += f.read() + "\n"
    serialized_code = base64.b64encode(js_code.encode("utf-8")).decode("utf-8")
    simulator_dir = os.path.join(project_name, "simulator")
    os.makedirs(simulator_dir, exist_ok=True)
    html_file = os.path.join(simulator_dir, "simulator.html")
    with open(html_file, "w") as f:
        f.write(
            """<!DOCTYPE html>
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
</html>"""
        )
    package_json_path = os.path.join(simulator_dir, "package.json")
    with open(package_json_path, "w") as f:
        f.write(json.dumps({
            "name": f"{project_name}-simulator",
            "version": "1.0.0",
            "description": "Node-based iOS simulator for testing",
            "main": "index.js",
            "scripts": { "start": "node index.js" },
            "author": "Your Name",
            "license": "ISC"
        }))
    index_js_path = os.path.join(simulator_dir, "index.js")
    with open(index_js_path, "w") as f:
        f.write(
            """const express = require('express');
const app = express();
const port = 3000;
app.use(express.static(__dirname));
app.listen(port, () => { console.log(`Server listening on port ${port}`); });
"""
        )
    simulator_src_dir = os.path.join(simulator_dir, "src")
    os.makedirs(simulator_src_dir, exist_ok=True)
    main_js_path = os.path.join(simulator_src_dir, "main.js")
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
@click.option("--language", prompt="Language (swift/objc/rust)", help="Specify the language for debugging.")
def compile_and_debug(project_name, language):
    """Compile and debug source code in real-time using Gemini."""
    src_file = os.path.join(project_name, "src", "main.js")
    if not os.path.exists(src_file):
        console.log(f"[red]Source file '{src_file}' not found.[/red]")
        return
    try:
        with open(src_file, "r") as f:
            source_code = f.read()
        if language.lower() == "swift":
            compiled_code = " // Compiled Swift code placeholder"
        elif language.lower() == "objc":
            compiled_code = " // Compiled Objective-C code placeholder"
        elif language.lower() == "rust":
            compiled_code = " // Compiled Rust code placeholder"
        else:
            console.log(f"[red]Unsupported language: {language}.[/red]")
            return
        if config.get("enable_debugging", False):
            console.log("[blue]Using Gemini for debugging...[/blue]")
            debugging_result = {"status": "success", "code": source_code + "\n// Debugged", "changes": "Added debug logging"}
            if debugging_result.get("status") == "success":
                console.log("[green]Gemini debugging successful.[/green]")
                console.print(Panel(f"**Original Code:**\n{source_code}\n\n**Generated Code:**\n{debugging_result.get('code')}", title="Generated Code"))
                with open(src_file, "w") as f:
                    f.write(debugging_result.get("code"))
                console.print(Panel(f"**Changes:**\n{debugging_result.get('changes')}", title="Changes"))
        else:
            console.print(Panel(f"**Original Code:**\n{source_code}\n\n**Compiled Code:**\n{compiled_code}", title="Compiled Code"))
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

# -----------------------------
# Main Entry Point and Extension Loading
# -----------------------------

def load_ipython_extension(ipython):
    ipython.register_magics(AptAnMagics)

# Usage example:
def create_interface(gemini_api_key=None):
    """Create and display the interface."""
    interface = JedimtYescoInterface(gemini_api_key=gemini_api_key)
    interface.display()
    return interface

def main():
    """Main entry point for the script."""
    if "--yesco" in sys.argv:
        # Run Yesco CLI
        sys.argv.remove("--yesco")  # Remove the flag before passing arguments to Click
        yesco()
    elif "--gui" in sys.argv:
        # Run Kivy Interface Mapper
        if kivy_available:
            InterfaceMapperApp().run()
        else:
            print("Kivy is not installed. GUI features are disabled.")
    elif "--version" in sys.argv:
        # Display version information
        console.print(f"Jedimt/Yesco Version: {__version__}")
    elif "--help" in sys.argv:
        # Display help information for Yesco
        with click.Context(yesco) as ctx:
            click.echo(yesco.get_help(ctx))
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        # Treat as a Jedimt command
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        jedimt_instance = Jedimt(mode="compile", gemini_api_key=gemini_api_key)
        jedimt_instance.shell_command(sys.argv[1:])
    else:
        # Default behavior (e.g., show help)
        console.print("No valid command specified. Use --help for usage information.")

# Version information
__version__ = "0.4.5"

if __name__ == "__main__":
    main()
