from typing import Optional

import typer
from rich import print as rprint
from typing_extensions import Annotated
from zeep import Client

from . import __version__

URL_WSDL = "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL"

app = typer.Typer()


def find_country(lista_paises, codigo_iso):
    for elemento in lista_paises:
        if elemento["sISOCode"] == codigo_iso:
            return elemento["sName"]
    return None


def version_callback(value: bool):
    """Callback de mostrado de la versión"""

    if value:
        print(f"Capital SOAP v{__version__}")
        raise typer.Exit()


@app.command()
def main(
    country_iso_code: Annotated[
        str, typer.Argument(..., help="ISO code for country to find")
    ],
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", callback=version_callback, help="Show version.", is_eager=True
        ),
    ] = None,
):
    """Find the capital of a country"""

    client = Client(URL_WSDL)
    capital = client.service.CapitalCity(country_iso_code)
    if capital == "Country not found in the database":
        rprint(
            f"[bold yellow]Sorry!![/bold yellow] I can't find {country_iso_code} in my countries database"
        )
        exit(1)
    country_list = client.service.ListOfCountryNamesByName()
    country = find_country(country_list, country_iso_code)
    rprint(f"The capital of [green]{country} is {capital}[/green]")
    rprint("Demo with love :purple_heart:")


if __name__ == "__main__":
    app()
