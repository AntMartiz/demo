#!/usr/bin/env python3
"""
Script chapuza para actualizar la versión del proyecto.

Actualiza:
- En el archivo pyproject.toml la clave "version" de la tabla [project]
- En el archivo mkdocs.yml la clave "version" del objeto extra
- En el archivo __init__.py del módulo principal la variable __version__

Uso:
    python bump-version.py <nueva_version>
"""

import os
import re
import subprocess
import sys

MAIN_MODULE = "demo"


def update_pyproject_toml(new_version, filepath="pyproject.toml"):
    if not os.path.exists(filepath):
        print(f"Archivo {filepath} no encontrado.")
        return

    with open(filepath, "r", encoding="utf8") as f:
        content = f.read()

    # Definición del patrón para la búsqueda de la clave version
    # Se busca un patrón que coincida con 'version = "valor"'
    pattern = r'(^version\s=\s)(")[^"]*?(")\s*$'

    # Para limitar la actualización a la sección [project], separamos el contenido
    # Para ello, buscamos la posición de la tabla [project] y su final
    match_project = re.search(r"(?ms)^\s*\[project\](.*?)^\s*(\[|$)", content)
    if not match_project:
        print("No se encontró la sección [project] en pyproject.toml")
        return

    project_section = match_project.group(1)

    # Actualizamos la clave version en esa sección
    def repl(m):
        return m.group(1) + f'"{new_version}"'

    project_section_updated, count = re.subn(
        pattern, repl, project_section, flags=re.MULTILINE
    )

    if count == 0:
        print("No se encontró la clave version en pyproject.toml, sin cambios")
        return

    # Reconstruimos el contenido con la nueva sección
    content_updated = (
        content[: match_project.start(1)]
        + project_section_updated
        + content[match_project.end(1) :]
    )

    with open(filepath, "w", encoding="utf8") as f:
        f.write(content_updated)
    print(f"Actualizado {filepath}")


def update_mkdocs_yml(new_version, filepath="mkdocs.yml"):
    if not os.path.exists(filepath):
        print(f"Archivo {filepath} no encontrado.")
        return

    with open(filepath, "r", encoding="utf8") as f:
        lines = f.readlines()

    new_lines = []
    in_extra = False
    extra_indent = ""
    version_updated = False
    for line in lines:
        # Determinar si entramos en bloque extra
        if re.match(r"^extra:\s*$", line):
            in_extra = True
            # Se guardará la indentación de la siguiente línea que pertenezca al bloque
            new_lines.append(line)
            continue

        # Si estamos en bloque extra, comprobamos si se trata de la clave version
        if in_extra:
            # Si la línea es vacía o tiene indentación superior a la esperada, se asume que sigue en bloque
            indent_match = re.match(r"^(\s+)", line)
            if indent_match:
                indent = indent_match.group(1)
                # Si esta es la primera línea dentro de extra, guardamos la indentación
                if not extra_indent:
                    extra_indent = indent
                # Si coincide la indentación, buscamos la clave version
                if re.match(rf"^{re.escape(extra_indent)}version\s*:", line):
                    # Actualizamos la línea
                    line = re.sub(r"(:\s*).*$", rf'\1"{new_version}"', line)
                    version_updated = True
                    in_extra = False  # suponemos que la clave version es la única que actualizamos en extra
            else:
                # Si no hay indentación, puede que hayamos salido del bloque
                in_extra = False
        new_lines.append(line)

    if not version_updated:
        print("No se encontró la clave version en mkdocs.yml, sin cambios")
        return

    with open(filepath, "w", encoding="utf8") as f:
        f.writelines(new_lines)
    print(f"Actualizado {filepath}")


def update_init_py(new_version, filepath=os.path.join(MAIN_MODULE, "__init__.py")):
    if not os.path.exists(filepath):
        print(f"Archivo {filepath} no encontrado.")
        return

    with open(filepath, "r", encoding="utf8") as f:
        content = f.read()

    # Actualizamos líneas que tengan: __version__ = "..." o similar
    pattern = r'(^__version__\s=\s)(["\'])(.*?)\2'

    # Se utiliza una función para inyectar la nueva versión
    def version_replace(match):
        return f'{match.group(1)}"{new_version}"'

    content_updated, count = re.subn(
        pattern, version_replace, content, flags=re.MULTILINE
    )
    if count == 0:
        print(
            "No se encontró la variable __version__ en el módulo principal, sin cambios"
        )
        return

    with open(filepath, "w", encoding="utf8") as f:
        f.write(content_updated)
    print(f"Actualizado {filepath}")


def update_uv_lock():
    try:
        # Ejecuta el comando "uv sync" para que actualice uv.lock
        subprocess.run(
            ["uv", "sync"],
            check=True,  # Lanza una excepción si el comando falla
            capture_output=True,  # Captura la salida estándar y de error
            text=True,  # Devuelve los resultados como cadenas de texto
        )
        print("Actualizado uv.lock")

    except subprocess.CalledProcessError as e:
        print("Error al lanzar 'uv sync' para actualizar uv.lock:")
        print(e.stderr)


def main():
    if len(sys.argv) != 2:
        print("Uso: python bump-version.py <nueva_version>")
        sys.exit(1)

    new_version = sys.argv[1]
    update_pyproject_toml(new_version)
    update_mkdocs_yml(new_version)
    update_init_py(new_version)
    update_uv_lock()


if __name__ == "__main__":
    main()
