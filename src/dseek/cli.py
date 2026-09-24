import typer

app = typer.Typer(help="Disguise-and-Seek CLI")

@app.command()
def hello(name: str = "World"):
    """Hello command for testing."""
    typer.echo(f"Hello {name}")

if __name__ == "__main__":
    app()
