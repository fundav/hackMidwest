def scrape_current_page(USDA, By):
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
		fields['program_overview'] = USDA.find_element(By.CSS_SELECTOR, "#overview > div > div").text
	except Exception:
		fields['program_overview'] = None
	try:
		fields['program_overview_link'] = USDA.find_element(By.CSS_SELECTOR, "#overview > div > div > div > div > span > span > div > div > p > a").get_attribute('href')
	except Exception:
		fields['program_overview_link'] = None
	try:
		fields['program_apply'] = USDA.find_element(By.CSS_SELECTOR, "#to-apply").text
	except Exception:
		fields['program_apply'] = None
	try:
		fields['program_requirements'] = USDA.find_element(By.CSS_SELECTOR, "#other-requirements > div > div > div > div > div > div > p").text
	except Exception:
		fields['program_requirements'] = None
	try:
		fields['program_contact'] = USDA.find_element(By.CSS_SELECTOR, "#contact > div > div > div > div > div > div > p:nth-child(5)").text
	except Exception:
		fields['program_contact'] = None
	try:
		fields['program_contact_link'] = USDA.find_element(By.CSS_SELECTOR, "#contact > div > div > div > div > div > div > p:nth-child(5) a").get_attribute('href')
	except Exception:
		fields['program_contact_link'] = None
	try:
		fields['program_events'] = USDA.find_element(By.CSS_SELECTOR, "#events").text
	except Exception:
		fields['program_events'] = None
	return fields

# #contact info (county - phone number) (not working)
# # requirements (not working)... links to other pages (not working)
# # program events (not working)
# # program apply (not working)
# #program overview link (not working)
# #elibility
# #next steps