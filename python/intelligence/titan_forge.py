import os
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

class ASTValidator:
    """Validates the syntax of generated Python code via the Abstract Syntax Tree."""
    @staticmethod
    def is_valid_python(source_code: str) -> bool:
        try:
            ast.parse(source_code)
            return True
        except SyntaxError as e:
            print(f"[AST Validator] Syntax Error detected: {e}")
            return False

class SovereignAlgorithmicForge:
    """
    Sovereign Algorithmic Forge (Production House)
    A highly advanced, template-based, intelligent generator that uses combinatorics,
    workflows, and algorithmic substitution to construct massive, syntactically valid codebases,
    moving beyond black-box AI reliance.
    """
    def __init__(self, workspace_root: str):
        self.root = Path(workspace_root)
        self.blueprints_dir = self.root / "python" / "intelligence" / "forge_blueprints"
        self.blueprints_dir.mkdir(parents=True, exist_ok=True)
        
    def _synthesize_cpp(self, template_args: Dict[str, Any]) -> str:
        """Algorithmic C++ synthesis."""
        class_name = template_args.get("class_name", "UnknownClass")
        namespace = template_args.get("namespace", "sovereign::core")
        includes = "\n".join([f"#include <{inc}>" for inc in template_args.get("includes", [])])
        
        methods = ""
        for m in template_args.get("methods", []):
            ret = m.get("return", "void")
            name = m.get("name", "func")
            args = m.get("args", "")
            body = m.get("body", "")
            methods += f"    {ret} {name}({args}) {{\n        {body}\n    }}\n\n"
            
        return f"""// [SOVEREIGN FORGE] Algorithmic C++ Synthesis
// Namespace: {namespace} | Class: {class_name}

{includes}

namespace {namespace} {{

class {class_name} {{
public:
{methods}
}};

}} // namespace {namespace}
"""

    def _synthesize_python(self, template_args: Dict[str, Any]) -> str:
        """Algorithmic Python synthesis."""
        imports = "\n".join([f"import {imp}" for imp in template_args.get("imports", [])])
        from_imports = "\n".join([f"from {frm} import {imp}" for frm, imp in template_args.get("from_imports", [])])
        
        classes = ""
        for cls in template_args.get("classes", []):
            c_name = cls.get("name", "GeneratedClass")
            c_base = f"({cls['base']})" if "base" in cls else ""
            classes += f"\nclass {c_name}{c_base}:\n"
            for m in cls.get("methods", []):
                args = m.get("args", "self")
                body = m.get("body", "pass").replace("\n", "\n        ")
                classes += f"    def {m['name']}({args}):\n        {body}\n\n"
                
        functions = ""
        for f in template_args.get("functions", []):
            args = f.get("args", "")
            body = f.get("body", "pass").replace("\n", "\n    ")
            decorators = "".join([f"@{dec}\n" for dec in f.get("decorators", [])])
            functions += f"\n{decorators}def {f['name']}({args}):\n    {body}\n"

        return f'''"""
[SOVEREIGN FORGE] Algorithmic Python Synthesis
"""
{imports}
{from_imports}
{classes}
{functions}
'''

    def generate_from_blueprint(self, blueprint_file: str):
        """Reads a JSON blueprint and generates the entire architectural module."""
        bp_path = self.blueprints_dir / blueprint_file
        if not bp_path.exists():
            print(f"[Forge] Blueprint {blueprint_file} not found.")
            return

        print(f"\n=============================================")
        print(f" EXECUTING BLUEPRINT: {blueprint_file}")
        print(f"=============================================")

        with open(bp_path, "r", encoding="utf-8") as f:
            blueprint = json.load(f)
            
        for file_info in blueprint.get("files", []):
            target_rel_path = file_info["path"]
            lang = file_info["language"]
            args = file_info["template_args"]
            
            target_path = self.root / target_rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"[Forge] Synthesizing {target_rel_path} ({lang})...")
            
            if lang == "cpp" or lang == "hpp":
                code = self._synthesize_cpp(args)
                with open(target_path, "w", encoding="utf-8") as out:
                    out.write(code)
                print(f"[Forge] Wrote C++ to {target_path}")
                
            elif lang == "python":
                code = self._synthesize_python(args)
                if ASTValidator.is_valid_python(code):
                    with open(target_path, "w", encoding="utf-8") as out:
                        out.write(code)
                    print(f"[Forge] AST Validated! Wrote Python to {target_path}")
                else:
                    print(f"[Forge] SYNTAX ERROR in generated Python for {target_rel_path}. Code discarded.")
                    
        self._auto_commit(blueprint.get("name", blueprint_file))

    def _auto_commit(self, module_name: str):
        """Automatically commits the generated code to git if available."""
        try:
            print(f"[Forge] Auto-committing {module_name} to version control...")
            subprocess.run(["git", "add", "."], cwd=self.root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"[Forge] Synthesized {module_name} architecture"], cwd=self.root, check=True, capture_output=True)
            print(f"[Forge] Git commit successful.")
        except Exception as e:
            print(f"[Forge] Auto-commit skipped (not a git repo or no changes).")

if __name__ == "__main__":
    workspace = r"C:\Users\Medin\OneDrive\Documents\AIEOSpro"
    forge = SovereignAlgorithmicForge(workspace)
    
    # If this script is run directly, it will look for blueprints in python/intelligence/forge_blueprints/
    for bp in forge.blueprints_dir.glob("*.json"):
        forge.generate_from_blueprint(bp.name)
