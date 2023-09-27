#manifest code isn't working with new quiz imports
#eventually need other question types to be supported

import pandas as pd
from lxml import etree
import zipfile
import urllib.parse
import hashlib
import html


# Save the XML file to a ZIP file
def save_to_zip(xml_tree, output_path):
    with zipfile.ZipFile(output_path, "w") as zf:
        xml_str = etree.tostring(xml_tree, encoding="ISO-8859-1", pretty_print=True)
        zf.writestr("qti_questions.xml", xml_str)

def save_xml_to_zip(qti_xml, assessment_id, manifest_xml, output_zip, image_files=[]):
    with zipfile.ZipFile(output_zip, "w") as zf:
        # Write the manifest XML file to the zip
        zf.writestr("imsmanifest.xml", manifest_xml)

        # Write the QTI XML to the zip
        qti_xml_str = etree.tostring(qti_xml, encoding="ISO-8859-1", pretty_print=True)
        zf.writestr(f"{assessment_id}/{assessment_id}.xml", qti_xml_str)

        # Write image files to the "Uploaded Media" folder in the zip if there are any
        for image_file in image_files:
            zf.write(image_file, f"Uploaded Media/{image_file}")
            
    return 0

def create_qti_xml(questions_df,basename, assessment_ident):
    xmlns = "http://www.imsglobal.org/xsd/ims_qtiasiv2p1"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    schema_location = "http://www.imsglobal.org/xsd/ims_qtiasiv2p1 http://www.imsglobal.org/xsd/ims_qtiasiv2p1.xsd"

    questestinterop = etree.Element("questestinterop", nsmap={None: xmlns, "xsi": xsi}, attrib={"{"+xsi+"}schemaLocation": schema_location})
    assessment = etree.SubElement(questestinterop, "assessment", attrib={"ident": assessment_ident, "title": basename})

    qtimetadata = etree.SubElement(assessment, "qtimetadata")
    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "cc_maxattempts"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = "1"

    section = etree.SubElement(assessment, "section", attrib={"ident": "root_section"})

    for index, row in questions_df.iterrows():
        question_type = row['question_type']

        item = etree.SubElement(section, "item", attrib={"ident": assessment_ident+f"_i{index}", "title": basename+f"_Q{index + 1}"})
        
        if question_type == 'short_answer':
            handle_short_answer_question(row, item, index)
        elif question_type == 'multiple_choice':
            handle_multiple_choice_question(row, item, index)
        elif question_type == 'true_false':
            handle_true_false_question(row, item, index)
        elif question_type == 'multi_select':
            handle_multi_select_question(row, item, index)
        elif question_type == 'numerical_tolerance':
            handle_numerical_tolerance_question(row, item, index)
        elif question_type == 'numerical_range':
            handle_numerical_range_question(row, item, index)
        else:
            print(f"Unknown question type: {question_type}")

    
    return questestinterop

def create_img_mattext(image_file):
    image_tag = f'<img src="$IMS-CC-FILEBASE$/Uploaded%20Media/{image_file}" alt="{image_file}">'
    mattext = f'<mattext texttype="text/html">{image_tag}</mattext>'
    return mattext

def create_mattext_element(latex_code):
    base_url = "https://weber.instructure.com/equation_images/"
    scale = "1.5"
    img_src = f"{base_url}{urllib.parse.quote_plus(latex_code)}?scale={scale}"
    mattext = f'<mattext texttype="text/html"><img class="equation_image" title="{latex_code}" src="{img_src}" alt="LaTeX: {latex_code}" data-equation-content="{latex_code}" data-ignore-a11y-check=""></mattext>'
    return mattext


def create_manifest_xml(assessment_ident, assessment_title, image_files=[]):    #manifests aren't needed for generating banks in Classic Canvas Quizzes. They're needed for New Canvas Quizzes (2023) 
    # Register the namespaces
    etree.register_namespace("ims", "http://www.imsglobal.org/xsd/imscp_v1p1")
    etree.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
    etree.register_namespace("imsqti", "http://www.imsglobal.org/xsd/imsqti_v2p1")

    # Create the root element with the proper namespace
    imsmanifest = etree.Element(etree.QName("http://www.imsglobal.org/xsd/imscp_v1p1", "imsmanifest"), attrib={
        "{" + "http://www.w3.org/2001/XMLSchema-instance" + "}schemaLocation":
            "http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/qtiv2p1_imscpv1p2_v1p0.xsd"
    })

    organizations = etree.SubElement(imsmanifest, "organizations")
    organization = etree.SubElement(organizations, "organization")
    organization.set("identifier", "org1")

    item = etree.SubElement(organization, "item")
    item.set("identifier", "assessment")
    item.set("identifierref", assessment_ident)

    resources = etree.SubElement(imsmanifest, "resources")
    resource = etree.SubElement(resources, "resource")
    resource.set("identifier", assessment_ident)
    resource.set("type", 'imsqti_test_xmlv2p1')
    resource.set("href", assessment_ident+".xml")

    # Adding image files and their dependencies
    for image_file in image_files:
        image_id = "img" + image_file.replace(" ", "").replace(".", "")

        image_resource = etree.SubElement(resources, "resource")
        image_resource.set("identifier", image_id)
        image_resource.set("type", "webcontent")
        image_resource.set("href", "Uploaded Media/" + image_file)

        file_elem = etree.SubElement(image_resource, "file")
        file_elem.set("href", "Uploaded Media/" + image_file)

        # Add dependency to assessment item
        dependency_elem = etree.SubElement(resource, "dependency")
        dependency_elem.set("identifierref", image_id)

    # Convert the XML structure to a string
    manifest_xml = etree.tostring(imsmanifest, encoding="UTF-8", method="xml", pretty_print=True).decode("UTF-8")

    return manifest_xml

def handle_short_answer_question(row, item, index):
    itemmetadata = etree.SubElement(item, "itemmetadata")
    qtimetadata = etree.SubElement(itemmetadata, "qtimetadata")
    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "question_type"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = "short_answer_question"

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "points_possible"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = "1.0"

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "original_answer_ids"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "assessment_question_identifierref"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = f"i{index:012}_id"

    presentation = etree.SubElement(item, "presentation")
    material = etree.SubElement(presentation, "material")
    mattext = etree.SubElement(material, "mattext", attrib={"texttype": "text/html"})
    mattext.text = row['question']
    response_str = etree.SubElement(presentation, "response_str", attrib={"ident" : "response1", "rcardinality" : "Single"})
    render_fib = etree.SubElement(response_str, "render_fib")
    response_label = etree.SubElement(render_fib, "response_label", attrib={"ident":"answer1","rshuffle":"No"})
    
    resprocessing = etree.SubElement(item, "resprocessing")
    outcomes = etree.SubElement(resprocessing, "outcomes")
    decvar = etree.SubElement(outcomes, "decvar", attrib={"maxvalue":"100","minvalue":"0","varname":"SCORE","vartype":"Decimal"})
    respcondition = etree.SubElement(resprocessing, "respcondition", attrib={"continue":"No"})
    conditionvar = etree.SubElement(respcondition, "conditionvar")
    if isinstance(row["correct_answers"], str):
        for answer in row["correct_answers"].split(";"):
            varequal = etree.SubElement(conditionvar, "varequal", attrib={"respident":"response1"})
            varequal.text = answer
    else:
        varequal = etree.SubElement(conditionvar, "varequal", attrib={"respident":"response1"})
        varequal.text = str(row["correct_answers"])

    setvar = etree.SubElement(respcondition, "setvar", attrib={"action":"Set","varname":"SCORE"})
    setvar.text = "100"
    
def handle_multiple_choice_question(row, item, index):
    correct_answers = row['correct_answers'].split(';')
    incorrect_answers = row['incorrect_answers'].split(';') if 'incorrect_answers' in row else []

    itemmetadata = etree.SubElement(item, "itemmetadata")
    qtimetadata = etree.SubElement(itemmetadata, "qtimetadata")

    # Add metadata fields manually
    for label, entry in [("question_type", "multiple_choice_question"), ("points_possible", "1.0"),
                         ("original_answer_ids", ",".join([str(i) for i in range(index * 10, index * 10 + len(correct_answers) + len(incorrect_answers))])),
                         ("assessment_question_identifierref", "gde73a1187d871ebab8ee8ec7b3e10a9a")]:
        qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
        fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
        fieldlabel.text = label
        fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
        fieldentry.text = entry

    # Create the question presentation
    presentation = etree.SubElement(item, "presentation")
    material = etree.SubElement(presentation, "material")
    mattext = etree.SubElement(material, "mattext", attrib={"texttype": "text/html"})
    mattext.text = row['question']

    # Create the response_lid and render_choice for the multiple choice question
    response_lid = etree.SubElement(presentation, "response_lid", attrib={"ident": "response1", "rcardinality": "Single"})
    render_choice = etree.SubElement(response_lid, "render_choice")

    # Loop over all answers (correct and incorrect) to create response_labels
    all_answers = correct_answers + incorrect_answers
    for i, answer in enumerate(all_answers):
        response_label = etree.SubElement(render_choice, "response_label", attrib={"ident": str(i + 1)})
        material = etree.SubElement(response_label, "material")
        mattext = etree.SubElement(material, "mattext", attrib={"texttype": "text/plain"})
        mattext.text = answer

    # Create resprocessing section
    resprocessing = etree.SubElement(item, "resprocessing")
    outcomes = etree.SubElement(resprocessing, "outcomes")
    decvar = etree.SubElement(outcomes, "decvar", attrib={"maxvalue": "100", "minvalue": "0", "varname": "SCORE", "vartype": "Decimal"})

    # Loop over correct answers to add the correct answer conditions to the resprocessing section
    for i, _ in enumerate(correct_answers):
        respcondition = etree.SubElement(resprocessing, "respcondition", attrib={"continue": "No"})
        conditionvar = etree.SubElement(respcondition, "conditionvar")
        varequal = etree.SubElement(conditionvar, "varequal", attrib={"respident": "response1"})
        varequal.text = str(i + 1)  # We start identifiers at 1
        setvar = etree.SubElement(respcondition, "setvar", attrib={"action": "Set", "varname": "SCORE"})
        setvar.text = "100"


def handle_true_false_question(row, item, index):
    # Add metadata
    itemmetadata = etree.SubElement(item, "itemmetadata")
    qtimetadata = etree.SubElement(itemmetadata, "qtimetadata")

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "question_type"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = "true_false_question"

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "points_possible"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = "1.0"

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "original_answer_ids"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = '6919' if row["correct_answers"] == 'True' else '6005'

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "assessment_question_identifierref"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = f"i{index:012}_id"

    # Add presentation
    presentation = etree.SubElement(item, "presentation")
    material = etree.SubElement(presentation, "material")
    mattext = etree.SubElement(material, "mattext", attrib={"texttype": "text/html"})
    mattext.text = row['question']

    response_lid = etree.SubElement(presentation, "response_lid", attrib={"ident" : "response1", "rcardinality" : "Single"})
    render_choice = etree.SubElement(response_lid, "render_choice")

    for i, choice in enumerate(["True", "False"]):
        response_label = etree.SubElement(render_choice, "response_label", attrib={"ident": str(6919 if choice == 'True' else 6005)})
        material = etree.SubElement(response_label, "material")
        mattext = etree.SubElement(material, "mattext", attrib={"texttype": "text/plain"})
        mattext.text = choice

    # Add response processing
    resprocessing = etree.SubElement(item, "resprocessing")
    outcomes = etree.SubElement(resprocessing, "outcomes")
    decvar = etree.SubElement(outcomes, "decvar", attrib={"maxvalue":"100","minvalue":"0","varname":"SCORE","vartype":"Decimal"})
    respcondition = etree.SubElement(resprocessing, "respcondition", attrib={"continue":"No"})
    conditionvar = etree.SubElement(respcondition, "conditionvar")
    
    varequal = etree.SubElement(conditionvar, "varequal", attrib={"respident":"response1"})
    varequal.text = '6919' if row["correct_answers"] == 'True' else '6005'

    setvar = etree.SubElement(respcondition, "setvar", attrib={"action":"Set","varname":"SCORE"})
    setvar.text = "100"

def handle_multi_select_question(row, item, index):
    # Add metadata
    itemmetadata = etree.SubElement(item, "itemmetadata")
    qtimetadata = etree.SubElement(itemmetadata, "qtimetadata")

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "question_type"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = "multiple_answers_question"

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "points_possible"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = "1.0"

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "original_answer_ids"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = ','.join([hashlib.md5(answer.encode()).hexdigest() for answer in row["correct_answers"]+row["incorrect_answers"]])

    qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
    fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
    fieldlabel.text = "assessment_question_identifierref"
    fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
    fieldentry.text = f"i{index:012}_id"

    # Add presentation
    presentation = etree.SubElement(item, "presentation")
    material = etree.SubElement(presentation, "material")
    mattext = etree.SubElement(material, "mattext", attrib={"texttype": "text/html"})
    mattext.text = row['question']

    response_lid = etree.SubElement(presentation, "response_lid", attrib={"ident" : "response1", "rcardinality" : "Multiple"})
    render_choice = etree.SubElement(response_lid, "render_choice")

    for answer in row["correct_answers"]+row["incorrect_answers"]:
        response_label = etree.SubElement(render_choice, "response_label", attrib={"ident": hashlib.md5(answer.encode()).hexdigest()})
        material = etree.SubElement(response_label, "material")
        mattext = etree.SubElement(material, "mattext", attrib={"texttype": "text/plain"})
        mattext.text = answer

    # Add response processing
    resprocessing = etree.SubElement(item, "resprocessing")
    outcomes = etree.SubElement(resprocessing, "outcomes")
    decvar = etree.SubElement(outcomes, "decvar", attrib={"maxvalue":"100","minvalue":"0","varname":"SCORE","vartype":"Decimal"})
    respcondition = etree.SubElement(resprocessing, "respcondition", attrib={"continue":"No"})
    conditionvar = etree.SubElement(respcondition, "conditionvar")
    
    and_element = etree.SubElement(conditionvar, "and")
    
    for answer in row["correct_answers"]:
        varequal = etree.SubElement(and_element, "varequal", attrib={"respident":"response1"})
        varequal.text = hashlib.md5(answer.encode()).hexdigest()

    for answer in row["incorrect_answers"]:
        not_element = etree.SubElement(and_element, "not")
        varequal = etree.SubElement(not_element, "varequal", attrib={"respident":"response1"})
        varequal.text = hashlib.md5(answer.encode()).hexdigest()

    setvar = etree.SubElement(respcondition, "setvar", attrib={"action":"Set","varname":"SCORE"})
    setvar.text = "100"

def handle_numerical_tolerance_question(row, item, index):
    # Metadata
    itemmetadata = etree.SubElement(item, "itemmetadata")

    qtimetadata = etree.SubElement(itemmetadata, "qtimetadata")
    fieldlabels = ['question_type', 'points_possible', 'original_answer_ids', 'assessment_question_identifierref']
    fieldentries = ['numerical_question', "1.0", f"{index + 1}", f"Question{index + 1}"]
    for label, entry in zip(fieldlabels, fieldentries):
        qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
        fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
        fieldlabel.text = label
        fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
        fieldentry.text = entry

    # Presentation
    presentation = etree.SubElement(item, "presentation")
    material = etree.SubElement(presentation, "material")
    mattext = etree.SubElement(material, "mattext", attrib={"texttype": "text/html"})
    mattext.text = html.escape(row['question'])

    response_str = etree.SubElement(presentation, "response_str", attrib={"ident": "response1", "rcardinality": "Single"})
    render_fib = etree.SubElement(response_str, "render_fib", attrib={"fibtype": "Decimal"})
    response_label = etree.SubElement(render_fib, "response_label", attrib={"ident": "answer1"})

    # Response Processing
    resprocessing = etree.SubElement(item, "resprocessing")
    outcomes = etree.SubElement(resprocessing, "outcomes")
    decvar = etree.SubElement(outcomes, "decvar", attrib={"maxvalue": "100", "minvalue": "0", "varname": "SCORE", "vartype": "Decimal"})
    
    respcondition = etree.SubElement(resprocessing, "respcondition", attrib={"continue": "No"})
    conditionvar = etree.SubElement(respcondition, "conditionvar")
    answers = row['correct_answers'].split(';')
    or_elem = etree.SubElement(conditionvar, "or")
    for ans in answers:
        value, tolerance = ans.split(':')
        and_elem = etree.SubElement(or_elem, "and")
        vargte = etree.SubElement(and_elem, "vargte", attrib={"respident": "response1"})
        vargte.text = str(float(value) - float(tolerance))
        varlte = etree.SubElement(and_elem, "varlte", attrib={"respident": "response1"})
        varlte.text = str(float(value) + float(tolerance))
    setvar = etree.SubElement(respcondition, "setvar", attrib={"action": "Set", "varname": "SCORE"})
    setvar.text = "100"


def handle_numerical_range_question(row, item, index):
    itemmetadata = etree.SubElement(item, "itemmetadata")
    qtimetadata = etree.SubElement(itemmetadata, "qtimetadata")
    
    fieldlabels = ['question_type', 'points_possible', 'original_answer_ids', 'assessment_question_identifierref']
    fieldentries = ['numerical_question', "1.0", f"{index + 1}", f"Question{index + 1}"]
    for label, entry in zip(fieldlabels, fieldentries):
        qtimetadatafield = etree.SubElement(qtimetadata, "qtimetadatafield")
        fieldlabel = etree.SubElement(qtimetadatafield, "fieldlabel")
        fieldlabel.text = label
        fieldentry = etree.SubElement(qtimetadatafield, "fieldentry")
        fieldentry.text = entry

    presentation = etree.SubElement(item, "presentation")
    material = etree.SubElement(presentation, "material")
    mattext = etree.SubElement(material, "mattext", attrib={"texttype": "text/html"})
    mattext.text = html.escape(row['question'])

    response_str = etree.SubElement(presentation, "response_str", attrib={"ident": "response1", "rcardinality": "Single"})
    render_fib = etree.SubElement(response_str, "render_fib", attrib={"fibtype": "Decimal"})
    response_label = etree.SubElement(render_fib, "response_label", attrib={"ident": "answer1"})

    resprocessing = etree.SubElement(item, "resprocessing")
    outcomes = etree.SubElement(resprocessing, "outcomes")
    decvar = etree.SubElement(outcomes, "decvar", attrib={"maxvalue": "100", "minvalue": "0", "varname": "SCORE", "vartype": "Decimal"})

    respcondition = etree.SubElement(resprocessing, "respcondition", attrib={"continue": "No"})
    conditionvar = etree.SubElement(respcondition, "conditionvar")
    
    correct_range = row['correct_answers'].split(';')
    lower_bound = correct_range[0]
    upper_bound = correct_range[1]
    
    vargte = etree.SubElement(conditionvar, "vargte", attrib={"respident": "response1"})
    vargte.text = lower_bound
    
    varlte = etree.SubElement(conditionvar, "varlte", attrib={"respident": "response1"})
    varlte.text = upper_bound

    setvar = etree.SubElement(respcondition, "setvar", attrib={"action": "Set", "varname": "SCORE"})
    setvar.text = "100"
