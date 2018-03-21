# -*- coding: utf-8 -*-
# Brewers Association Beer Style Guidelines for 2018
# Ugly/kludgy Beautiful Soup script but hey it works! 
# daniel.zenner@gmail.com 

from bs4 import BeautifulSoup
import requests
import json
import re
import collections


# Style Ordered Dictionary
style_template = collections.OrderedDict()
style_template['id'] = None
style_template['name'] = None
style_template['style-category'] = None 
style_template['style-origin'] = None
style_template['color'] = None
style_template['clarity'] = None
style_template['perceived_malt'] = None
style_template['perceived_hop'] = None
style_template['perceived_bitterness'] = None
style_template['fermentation'] = None
style_template['body'] = None
style_template['notes'] = None
style_template['og'] = None
style_template['og_plato'] = None
style_template['og_min'] = None
style_template['og_max'] = None   
style_template['og_min_plato'] = None
style_template['og_max_plato'] = None
style_template['fg'] = None
style_template['fg_plato'] = None
style_template['fg_min'] = None
style_template['fg_max'] = None
style_template['fg_min_plato'] = None
style_template['fg_max_plato'] = None
style_template['abw'] = None
style_template['abw_min'] = None
style_template['abw_max'] = None   
style_template['abv'] = None
style_template['abv_min'] = None
style_template['abv_max'] = None
style_template['ibu'] = None
style_template['ibu_min'] = None
style_template['ibu_max'] = None
style_template['color_srm'] = None
style_template['color_ebc'] = None
style_template['color_min_srm'] = None
style_template['color_max_srm'] = None
style_template['color_min_ebc'] = None
style_template['color_max_ebc'] = None   

desc_parts_map = {
    "color": "color", 
    "clarity": "clarity",
    "perceived malt aroma & flavor": "perceived_malt",
    "perceived hop aroma & flavor": "perceived_hop",
    "perceived bitterness": "perceived_bitterness",
    "fermentation characteristics": "fermentation",
    "body": "body", 
    "additional notes": "notes"
}

# All the styles yo!
all_ye_beer_styles = []


# Lets Roll!
r  = requests.get("https://www.brewersassociation.org/resources/brewers-association-beer-style-guidelines/")
data = r.text
soup = BeautifulSoup(data, "html.parser")
style_sections_raw = soup.find_all("section", id="styles")

# Used for style output
parent_style_cat = None
style_origin = None


if len(style_sections_raw):
    # Get all Parent Type Categories 
    style_groups_raw = style_sections_raw[1].find_all("div", class_="group")
    
    # Loop though Parent Types
    for group in style_groups_raw:
        
        parent_style_cat = group.find("h1").get_text()

        # Get all Style Origins for Parent 
        style_origin_raw = group.find_all("div", class_="origin")

        # Loop though Style Origins        
        for style_origins in style_origin_raw:
            style_origin = style_origins.find("h2").get_text() 

            # Got the styles!
            styles_raw = style_origins.find_all("div", class_="style")
            for style in styles_raw:
                style_dict = style_template.copy()
                
                style_description_raw = style.find("ul")
                style_details_raw = style.find("div", class_="full callout")
                
                style_dict['name'] = style.find("h3").get_text() 
                style_dict['id'] = int(style.find("h3")['id']) 
                style_dict['style-category'] = parent_style_cat
                style_dict['style-origin'] = style_origin
                
                for desc_part in style_description_raw.find_all("li"):
                    # Extract out part title
                    desc_title = desc_part.find("strong").get_text().strip().lower().replace(':','')

                    # Map title to field name
                    desc_part_field = desc_parts_map[desc_title]

                    style_dict[desc_part_field] = desc_part.strong.next_sibling.strip()

                for details in style_details_raw.find_all("strong"):
                    details_title = details.get_text().strip().lower()

                    if 'original gravity' in details_title:                        
                        og_raw = details.next_sibling.strip().encode("utf8")
                        og_match = re.findall(r'(\d?[0-9,\.]+-\d?[0-9,\.]+)', og_raw)
                        
                        if og_match:
                            style_dict['og'] = og_match[0]
                            og_parts = og_match[0].split('-')
                            if og_parts:
                                style_dict['og_min'] = float(og_parts[0])
                                style_dict['og_max'] = float(og_parts[1])
                            
                            style_dict['og_plato'] = og_match[1]
                            og_plato_parts = og_match[1].split('-')
                            if og_plato_parts:
                                style_dict['og_min_plato'] = float(og_plato_parts[0])
                                style_dict['og_max_plato'] = float(og_plato_parts[1])
                    
                    if 'apparent extract' in details_title:
                        fg_raw = details.next_sibling.strip().encode("utf8")
                        fg_match = re.findall(r'(\d?[0-9,\.]+-\d?[0-9,\.]+)', fg_raw)

                        if fg_match:
                            style_dict['fg'] = fg_match[0]
                            fg_parts = fg_match[0].split('-')
                            if fg_parts:
                                style_dict['fg_min'] = float(fg_parts[0])
                                style_dict['fg_max'] = float(fg_parts[1])
                            
                            style_dict['fg_plato'] = fg_match[1]
                            fg_plato_parts = fg_match[1].split('-')
                            if fg_plato_parts:
                                style_dict['fg_min_plato'] = float(fg_plato_parts[0])
                                style_dict['fg_max_plato'] = float(fg_plato_parts[1])

                    if 'alcohol by weight' in details_title:
                        alcohol_raw = details.next_sibling.strip().encode("utf8")
                        alcohol_match = re.findall(r'(\d?[0-9,\.]+%-\d[0-9,\.]+%)', alcohol_raw)

                        if alcohol_match:
                            style_dict['abw'] = alcohol_match[0]
                            abw_parts = alcohol_match[0].split('-')
                            if abw_parts:
                                style_dict['abw_min'] = abw_parts[0]
                                style_dict['abw_max'] = abw_parts[1]
                            
                            style_dict['abv'] = alcohol_match[1]
                            abv_parts = alcohol_match[1].split('-')
                            if abv_parts:
                                style_dict['abv_min'] = abv_parts[0]
                                style_dict['abv_max'] = abv_parts[1]
                    
                    if 'bitterness' in details_title: 
                        bitter_raw = details.next_sibling.strip().encode("utf8")
                        bitter_match = re.findall(r'(\d?[0-9,\.]+-\d[0-9,\.]+)', bitter_raw)

                        if bitter_match:
                            style_dict['ibu'] = bitter_match[0]
                            ibu_parts = bitter_match[0].split('-')
                            if abw_parts:
                                style_dict['ibu_min'] = int(ibu_parts[0])
                                style_dict['ibu_max'] = int(ibu_parts[1])

                    if 'color' in details_title: 
                        color_raw = details.next_sibling.strip().encode("utf8")
                        color_match = re.findall(r'(\d?[0-9,\.,\+]+-?\d?[0-9,\.,\+]+)', color_raw)

                        if color_match:
                            style_dict['color_srm'] = color_match[0]
                            srm_parts = color_match[0].split('-')
                            if len(abw_parts) < 1:
                                style_dict['color_min_srm'] = float(srm_parts[0])
                                style_dict['color_max_srm'] = float(srm_parts[1])
                            else:
                                style_dict['color_min_srm'] = float(srm_parts[0].replace('+',''))

                            style_dict['color_ebc'] = color_match[1]
                            ebc_parts = color_match[1].split('-')
                            if len(ebc_parts) < 1:
                                style_dict['color_min_ebc'] = float(ebc_parts[0])
                                style_dict['color_max_ebc'] = float(ebc_parts[1])
                            else:
                                style_dict['color_min_ebc'] = float(ebc_parts[0].replace('+',''))

                # Add Style to the list!
                all_ye_beer_styles.append(style_dict)

# Export
file = open('ba_beer_styles_2018.json','w') 
file.write(json.dumps(all_ye_beer_styles)) 
file.close() 
