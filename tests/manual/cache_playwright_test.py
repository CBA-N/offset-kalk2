import asyncio

from playwright.async_api import async_playwright, expect

async def run_scenario():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://127.0.0.1:7018/', wait_until='networkidle')
        await page.wait_for_selector('#kontrahent_id option[value="1"]', state='attached', timeout=10000)
        await page.wait_for_selector('#kategoriaPapieru option:not([value=""])', state='attached', timeout=10000)

        await page.fill('input[name="nazwa_produktu"]', 'Test cache produkt')
        await page.fill('input[name="naklad"]', '4321')
        await page.select_option('#rodzajPracy', value='Folder A4')
        await page.select_option('#kontrahent_id', value='2')

        await page.select_option('#kategoriaPapieru', value='Powlekany')
        await page.wait_for_selector('#rodzajPapieru:not([disabled]) option[value="Kreda błysk"]', state='attached', timeout=10000)
        await page.select_option('#rodzajPapieru', value='Kreda błysk')
        await page.wait_for_function('() => { const el = document.querySelector("#gramatura"); return el && !el.disabled && Array.from(el.options).some(o => o.value === "170"); }', timeout=10000)
        await page.select_option('#gramatura', value='170')

        await page.select_option('#kolorystyka', value='4+4')
        await page.fill('#iloscForm', '6')
        await page.uncheck('#wymagaCiecia')

        await page.check('input[name="kolory_specjalne"][value="Pantone Metallic"]')
        await page.check('input[name="uszlachetnienia"][value="Lakier UV wybiórczy"]')
        await page.check('input[name="obrobka"][value="Bigowanie"]')

        await page.select_option('select[name="pakowanie"]', value='Kartony indywidualne (po 100 szt)')
        await page.select_option('select[name="transport"]', value='Kurier paletowy (1 paleta)')
        await page.fill('input[name="marza_procent"]', '27')
        await page.select_option('select[name="priorytet_optymalizacji"]', value='Najniższy koszt')

        await page.wait_for_timeout(500)
        await page.click('a[href="/historia"]')
        await page.wait_for_url('**/historia', timeout=10000)

        await page.click('a[href="/"]')
        await page.wait_for_url('http://127.0.0.1:7018/', timeout=10000)
        await page.wait_for_selector('#kontrahent_id option[value="2"]', state='attached', timeout=10000)
        await page.wait_for_selector('#kategoriaPapieru option[value="Powlekany"]', state='attached', timeout=10000)

        await expect(page.locator('input[name="nazwa_produktu"]')).to_have_value('Test cache produkt', timeout=10000)
        await expect(page.locator('input[name="naklad"]')).to_have_value('4321', timeout=10000)
        await expect(page.locator('#rodzajPracy')).to_have_value('Folder A4', timeout=10000)
        await expect(page.locator('#kontrahent_id')).to_have_value('2', timeout=10000)
        await expect(page.locator('#kategoriaPapieru')).to_have_value('Powlekany', timeout=10000)
        await expect(page.locator('#rodzajPapieru')).to_have_value('Kreda błysk', timeout=10000)
        await expect(page.locator('#gramatura')).to_have_value('170', timeout=10000)
        await expect(page.locator('#kolorystyka')).to_have_value('4+4', timeout=10000)
        await expect(page.locator('#iloscForm')).to_have_value('6', timeout=10000)
        await expect(page.locator('#wymagaCiecia')).not_to_be_checked()
        await expect(page.locator('input[name="kolory_specjalne"][value="Pantone Metallic"]')).to_be_checked()
        await expect(page.locator('input[name="uszlachetnienia"][value="Lakier UV wybiórczy"]')).to_be_checked()
        await expect(page.locator('input[name="obrobka"][value="Bigowanie"]')).to_be_checked()
        await expect(page.locator('select[name="pakowanie"]')).to_have_value('Kartony indywidualne (po 100 szt)', timeout=10000)
        await expect(page.locator('select[name="transport"]')).to_have_value('Kurier paletowy (1 paleta)', timeout=10000)
        await expect(page.locator('input[name="marza_procent"]')).to_have_value('27', timeout=10000)
        await expect(page.locator('select[name="priorytet_optymalizacji"]')).to_have_value('Najniższy koszt', timeout=10000)

        cache_value = await page.evaluate('localStorage.getItem("kalkulatorFormCache")')
        print('Cache before clear:', cache_value)

        await page.click('#clearOfferBtn')
        await page.wait_for_timeout(500)

        await expect(page.locator('input[name="nazwa_produktu"]')).to_have_value('Mój wydruk', timeout=10000)
        await expect(page.locator('input[name="naklad"]')).to_have_value('1000', timeout=10000)
        await expect(page.locator('#rodzajPracy')).to_have_value('', timeout=10000)
        await expect(page.locator('#kategoriaPapieru')).to_have_value('', timeout=10000)
        await expect(page.locator('#rodzajPapieru')).to_have_value('', timeout=10000)
        await expect(page.locator('#rodzajPapieru')).to_be_disabled()
        await expect(page.locator('#gramatura')).to_have_value('', timeout=10000)
        await expect(page.locator('#gramatura')).to_be_disabled()
        await expect(page.locator('#kolorystyka')).to_have_value('4+0', timeout=10000)
        await expect(page.locator('#iloscForm')).to_have_value('1', timeout=10000)
        await expect(page.locator('#wymagaCiecia')).to_be_checked()
        await expect(page.locator('input[name="kolory_specjalne"][value="Pantone Metallic"]')).not_to_be_checked()
        await expect(page.locator('input[name="uszlachetnienia"][value="Lakier UV wybiórczy"]')).not_to_be_checked()
        await expect(page.locator('input[name="obrobka"][value="Bigowanie"]')).not_to_be_checked()
        await expect(page.locator('select[name="pakowanie"]')).to_have_value('Folia stretch (standard)', timeout=10000)
        await expect(page.locator('select[name="transport"]')).to_have_value('Kurier standardowy (do 30 kg)', timeout=10000)
        await expect(page.locator('input[name="marza_procent"]')).to_have_value('20', timeout=10000)
        await expect(page.locator('select[name="priorytet_optymalizacji"]')).to_have_value('Minimalizacja odpadów', timeout=10000)

        cache_after_clear = await page.evaluate('localStorage.getItem("kalkulatorFormCache")')
        paper_selection_after_clear = await page.evaluate('localStorage.getItem("kalkulatorPapierSelection")')
        print('Cache after clear:', cache_after_clear)
        print('Paper selection after clear:', paper_selection_after_clear)

        await browser.close()


def main():
    asyncio.run(run_scenario())


if __name__ == '__main__':
    main()
