import typer

from com_agent.chat.ingest import load_information

app = typer.Typer()


@app.command()
def load_info(
    markdown_file: str = typer.Argument(..., help="Path to the Markdown file to load"),
    chunk_size: int = typer.Option(1000, help="Size of text chunks"),
    chunk_overlap: int = typer.Option(0, help="Overlap between chunks"),
):
    """
    Load information from a Markdown file and store it in PGVector.
    """
    typer.echo(f"Loading information from {markdown_file}")
    load_information(markdown_file, chunk_size, chunk_overlap)
    typer.echo("Process completed.")


if __name__ == "__main__":
    app()
