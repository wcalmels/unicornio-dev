from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from cli.api_client import ApiError, UnicornioClient
from cli.config import clear_token, get_api_url, get_token, save_config
from cli.context import bundle_sources, detect_language, read_text_file

app = typer.Typer(
    name="unicornio",
    help="CLI de Unicornio Dev — asistente de desarrollo con IA.",
    no_args_is_help=True,
)
console = Console()


def _client() -> UnicornioClient:
    token = get_token()
    if not token:
        console.print("[red]No has iniciado sesión. Ejecuta: unicornio login[/red]")
        raise typer.Exit(1)
    return UnicornioClient(token=token)


def _print_result(title: str, content: str) -> None:
    console.print(f"\n[bold cyan]{title}[/bold cyan]\n")
    console.print(Markdown(content))


@app.command()
def login(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
) -> None:
    """Inicia sesión y guarda el token localmente."""
    client = UnicornioClient(token=None)
    try:
        token = client.login(email, password)
    except ApiError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    save_config(token=token)
    console.print(f"[green]Sesión iniciada. API: {get_api_url()}[/green]")


@app.command()
def register(
    email: str = typer.Option(..., prompt=True),
    name: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True),
) -> None:
    """Crea una cuenta nueva."""
    client = UnicornioClient(token=None)
    try:
        token = client.register(email, name, password)
    except ApiError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    save_config(token=token)
    console.print(f"[green]Cuenta creada. Bienvenido, {name}![/green]")


@app.command()
def logout() -> None:
    """Cierra la sesión local."""
    clear_token()
    console.print("[green]Sesión cerrada.[/green]")


@app.command("whoami")
def whoami() -> None:
    """Muestra el usuario autenticado."""
    try:
        user = _client().me()
    except ApiError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    console.print(f"[bold]{user['name']}[/bold] ({user['email']}) — plan {user['plan']}")


@app.command()
def config(
    api_url: str = typer.Option(..., "--api-url", help="URL base de la API"),
) -> None:
    """Configura la URL de la API."""
    save_config(api_url=api_url)
    console.print(f"[green]API configurada: {api_url}[/green]")


@app.command()
def architect(
    project: str = typer.Argument(..., help="Nombre del proyecto"),
    description: str = typer.Option(..., "--description", "-d", help="Descripción del proyecto"),
) -> None:
    """Analiza requisitos y propone arquitectura."""
    try:
        result = _client().architect(project, description)
    except ApiError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    _print_result("Análisis de arquitectura", result)


@app.command()
def refactor(
    path: Path = typer.Argument(..., help="Archivo o directorio"),
    language: str | None = typer.Option(None, "--language", "-l", help="Lenguaje del código"),
) -> None:
    """Refactoriza código desde un archivo o carpeta."""
    try:
        code, detected = bundle_sources(path.resolve())
        lang = language or detected
        result = _client().refactor(code, lang)
    except (ApiError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    _print_result(f"Refactor ({path})", result)


@app.command()
def debug(
    error: str = typer.Option(..., "--error", "-e", help="Mensaje de error"),
    context: str = typer.Option("", "--context", "-c", help="Contexto adicional"),
    file: Path | None = typer.Option(None, "--file", "-f", help="Archivo relacionado"),
) -> None:
    """Diagnostica un error."""
    extra = context
    if file:
        if not file.exists():
            console.print(f"[red]Archivo no encontrado: {file}[/red]")
            raise typer.Exit(1)
        content = read_text_file(file.resolve())
        extra = f"{context}\n\nArchivo {file}:\n```\n{content}\n```".strip()

    try:
        result = _client().debug(error, extra)
    except ApiError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    _print_result("Solución", result)


@app.command()
def audit(
    path: Path = typer.Argument(..., help="Archivo o directorio a auditar"),
    language: str | None = typer.Option(None, "--language", "-l"),
) -> None:
    """Audita seguridad de código."""
    try:
        code, detected = bundle_sources(path.resolve())
        lang = language or detected
        result = _client().security(code, lang)
    except (ApiError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    _print_result(f"Auditoría de seguridad ({path})", result)


@app.command()
def performance(
    path: Path = typer.Argument(..., help="Archivo o directorio a analizar"),
    language: str | None = typer.Option(None, "--language", "-l"),
) -> None:
    """Analiza performance de código."""
    try:
        code, detected = bundle_sources(path.resolve())
        lang = language or detected
        result = _client().performance(code, lang)
    except (ApiError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    _print_result(f"Análisis de performance ({path})", result)


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", min=1, max=200),
) -> None:
    """Muestra el historial de consultas."""
    try:
        items = _client().history(limit=limit)
    except ApiError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if not items:
        console.print("[yellow]No hay consultas en el historial.[/yellow]")
        return

    table = Table(title="Historial de consultas")
    table.add_column("ID", style="dim")
    table.add_column("Módulo")
    table.add_column("Fecha")
    table.add_column("Resumen")

    for item in items:
        summary = item["output_text"][:80].replace("\n", " ")
        table.add_row(
            str(item["id"]),
            item["module"],
            item["created_at"][:19],
            summary + ("..." if len(item["output_text"]) > 80 else ""),
        )

    console.print(table)


if __name__ == "__main__":
    app()
