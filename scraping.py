def scrape_current_page(USDA, By, link):
	fields = {}
	try:
		fields['title'] = USDA.find_element(By.CSS_SELECTOR, "#main-content > div > div > div > h1").text
	except Exception:
		fields['title'] = None
	try:
		fields['program_status'] = USDA.find_element(By.CSS_SELECTOR, "#block-usda-rd-uswds-2-content--2 > article > div.grid-row.bg-base-lighter.margin-top-2.padding-105.program-heading > div.desktop---grid-col-3.tablet---grid-col-4.grid-col-12.padding-05 > div").text
	except Exception:
		fields['program_status'] = None
	try:
		fields['program_deadline'] = USDA.find_element(By.CSS_SELECTOR, "#block-usda-rd-uswds-2-content--2 > article > div.grid-row.bg-base-lighter.margin-top-2.padding-105.program-heading > div.desktop---grid-col-9.tablet---grid-col-8.grid-col-12.padding-05 > div").text
	except Exception:
		fields['program_deadline'] = None
	try:
		USDA.navigate_to((link+"#overview"))
		fields['program_overview'] = USDA.find_element(By.CSS_SELECTOR, "#overview > div > div").text
	except Exception:
		fields['program_overview'] = None
	try:
		USDA.navigate_to((link+"#to-apply"))
		fields['program_apply'] = USDA.find_element(By.CSS_SELECTOR, "#to-apply").text
	except Exception:
		fields['program_apply'] = None
	try:
		USDA.navigate_to((link+"#other-requirements"))
		fields['program_requirements'] = USDA.find_element(By.CSS_SELECTOR, "#other-requirements > div > div > div > div > div > div > p").text
	except Exception:
		fields['program_requirements'] = None
	try:
		USDA.navigate_to((link+"#contact"))
		fields['program_contact'] = USDA.find_element(By.CSS_SELECTOR, "#contact > div > div > div > div > div > div > p:nth-child(5)").text
	except Exception:
		fields['program_contact'] = None
	try:
		USDA.navigate_to((link+"#contact"))
		fields['program_contact_link'] = USDA.find_element(By.CSS_SELECTOR, "#contact > div > div > div > div > div > div > p:nth-child(5) a").get_attribute('href')
	except Exception:
		fields['program_contact_link'] = None
	try:
		USDA.navigate_to((link+"#events"))
		fields['program_events'] = USDA.find_element(By.CSS_SELECTOR, "#events").text
	except Exception:
		fields['program_events'] = None
	return fields