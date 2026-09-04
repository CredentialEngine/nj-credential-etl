from bs4 import BeautifulSoup
import pandas as pd

# Sample HTML content
html_content = """
<h2>Explore Our Programs</h2>
<div class="row">
<div class="col-md-6">
<p><a href="https://www.camdencc.edu/program/returning-technicaltrade-professionals/">Apprenticeship Programs (Electrical, HVAC, Plumbing)</a></p>
<p><a href="https://www.camdencc.edu/program/automotive-technology-cti/">Automotive Technology</a></p>
<p><a href="https://www.camdencc.edu/program/uniform-construction-code-building-inspector/">Building Inspector</a></p>
<p><a href="https://www.camdencc.edu/program/business/">Business</a></p>
<p><a href="https://www.camdencc.edu/program/carpentry-technology/">Carpentry Technology</a></p>
<p><a href="https://www.camdencc.edu/program/certified-registered-medical-assistant/">Certified Medical Assistant</a></p>
<p>		<!--

<p><a href="/program/certified-nursing-aide-cna/">Certified Nursing Aide (CNA)</a></p>

--></p>
<p><a href="https://www.camdencc.edu/program/cosmetology/">Cosmetology/Hair Stylist</a></p>
<p><a href="https://www.camdencc.edu/program/nail-technician/">Nail Technician</a></p>
<p><a href="https://www.camdencc.edu/program/skin-care-esthetician/">Skin Care/Esthetician</a></p>
<p><a href="https://www.camdencc.edu/program/computer-technician-support-specialist-cti/">Computer Technician Support Specialist</a></p>
<p><a href="https://www.camdencc.edu/program/culinary-arts-baking-pastry/">Culinary Arts / Baking &amp; Pastry</a></p>
<p>		<!-- 

<p><a href="/product/dialysis-technician/">Dialysis Patient Care Technician</a></p>

 --></p>
<p><a href="https://www.camdencc.edu/program/uniform-construction-code-electrical-inspector/">Electrical Inspector</a></p>
<p><a href="https://www.camdencc.edu/program/electrical-residential/">Electrical Residential</a></p>
<p><a href="https://www.camdencc.edu/program/elevator-inspector-hhs/">Elevator Inspector</a></p>
<p></p></div>
<div class="col-md-6">
<p><a href="https://www.camdencc.edu/program/uniform-construction-code-fire-inspector/">Fire Inspector</a></p>
<p>                <!-- 

<p><a href="/program/healthcare/">Healthcare</a></p>

 --></p>
<p><a href="https://www.camdencc.edu/program/heating-ventilation-air-conditioning/">Heating, Ventilation &amp; Air Conditioning (HVAC)</a></p>
<p><a href="https://www.camdencc.edu/program/hydro-technology-plumbing/">Hydro Technology (Plumbing)</a></p>
<p><a href="https://www.camdencc.edu/program/microsoft-office/">Microsoft Office Specialist</a></p>
<p><a href="https://www.camdencc.edu/program/network-certification-comptia/">CompTIA Network+</a><a></a></p><a>
</a><p><a href="https://www.camdencc.edu/academics-1/trade-careers/online-training/">Online Programs</a></p>
<p><a href="https://www.camdencc.edu/program/patient-care-technician-formerly-mst/">Patient Care Technician</a></p>
<p><a href="https://www.camdencc.edu/program/pharmacy-technician/">Pharmacy Technician</a></p>
<p><a href="https://www.camdencc.edu/program/plumbing-inspector-ics/">Plumbing Inspector</a></p>
<p><a href="https://www.camdencc.edu/program/real-estate/">Real Estate</a></p>
<p><a href="https://www.camdencc.edu/program/security/">CompTIA Security+</a></p>
<p><a href="https://www.camdencc.edu/program/subcode-official/">Subcode Official</a></p>
<p><a href="https://www.camdencc.edu/program/technology-manufacturing/">Technology—Manufacturing</a></p>
<p><a href="https://www.camdencc.edu/program/animal-care-2/">Veterinary Assistant</a></p>
<p><a href="https://www.camdencc.edu/program/welding-technology/">Welding Technology </a></p>
<p></p></div>
</div>
"""

# Using BeautifulSoup to parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <a> tags within <p> tags and extract program names and URLs
programs = []
for p_tag in soup.find_all('p'):
    a_tag = p_tag.find('a')
    if a_tag and a_tag['href'].startswith('https'):  # Check if it's a valid URL
        program_name = a_tag.get_text(strip=True)
        program_url = a_tag['href']
        programs.append({'Program Name': program_name, 'Program URL': program_url})

# Create a DataFrame from the list of programs
df = pd.DataFrame(programs)

# Save the DataFrame to a CSV file
output_csv = 'program_details.csv'
df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"Data has been written to {output_csv}.")
