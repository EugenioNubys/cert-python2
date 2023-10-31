from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def ordina_robots():
    """
    Ordina robot dal sito RobotSpareBin Industries Inc.
    Salva l'ordine HTML in una ricevuta PDF.
    Allega al suddetto screenshot del robot ordinato
.   Crea ZIP di tutte le ricevute
    """
    apri_sito_web()
    tabellaCsv=scarica_file_ordini_e_ottieni_tabella()
    cicla_tabella_ordini(tabellaCsv)
    archivia_ricevute()


def apri_sito_web():
    """apre il browser e va al link"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
def scarica_file_ordini_e_ottieni_tabella():
    """download del file csv"""
    http=HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tabellaCsv=Tables().read_table_from_csv("orders.csv")
    return tabellaCsv

def cicla_tabella_ordini(tabellaCsv):
    """inserimento ordini"""
    for rigaTabella in tabellaCsv:
        page=browser.page()
        page.click("button:text('OK')")    
        page.select_option("#head", str(rigaTabella["Head"]))
        page.check("#id-body-" + str(rigaTabella["Body"]))
        page.fill("//html/body/div/div/div/div/div/form/div[3]/input", str(rigaTabella["Legs"]))
        page.fill("#address", rigaTabella['Address'])

        errore = True
        while errore:
            page.click("#order")
            errore=page.is_visible(".alert-danger")

        page.wait_for_selector("#receipt")
        salva_ricevuta(rigaTabella["Order number"])
        
        

        page.click("#order-another")
        

def salva_ricevuta(numeroOrdine):
    """salvataggio ricevute singole in sottocartella ricevute"""
    page=browser.page()
    ricevuta=page.locator("#receipt").inner_html()
    page.locator('#robot-preview-image').screenshot(path="output/ricevuta "+numeroOrdine+".png")
    
    pdf=PDF()
    
    pdf.html_to_pdf(ricevuta, "output/ricevute/ricevuta "+numeroOrdine+".pdf")
    listafile=[
            "output/ricevuta "+numeroOrdine+".png"
            ,]
    pdf.add_files_to_pdf(listafile, "output/ricevute/ricevuta "+numeroOrdine+".pdf", append=True)
        
def archivia_ricevute():
     """creazione zip"""
     archivio = Archive()
     archivio.archive_folder_with_zip("output/ricevute/", "output/ricevute.zip")
