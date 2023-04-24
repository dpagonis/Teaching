import pandas as pd
from lxml import etree
import zipfile


def main():
    basename = str(input("base name of csv (omit .csv extension): "))
    input_csv = basename+".csv"
    output_zip = basename+".zip" # Output ZIP file path
    #output_xml = "qti_questions.xml"

    questions_df = pd.read_csv(input_csv)
    qti_xml = create_qti_xml(questions_df, basename)
    save_to_zip(qti_xml, output_zip)
    #etree.ElementTree(qti_xml).write(output_xml, encoding="ISO-8859-1", pretty_print=True, xml_declaration=True)


# Save the XML file to a ZIP file
def save_to_zip(xml_tree, output_path):
    with zipfile.ZipFile(output_path, "w") as zf:
        xml_str = etree.tostring(xml_tree, encoding="ISO-8859-1", pretty_print=True)
        zf.writestr("qti_questions.xml", xml_str)

def save_xml_to_zip(qti_xml, assessment_id, manifest_xml, output_zip):
    with zipfile.ZipFile(output_zip, "w") as zf:
        zf.writestr("imsmanifest.xml", manifest_xml)
        qti_xml_str = etree.tostring(qti_xml, encoding="ISO-8859-1", pretty_print=True)
        zf.writestr(f"{assessment_id}.xml", qti_xml_str)
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
        item = etree.SubElement(section, "item", attrib={"ident": assessment_ident+f"_i{index}", "title": basename+f"_Q{index + 1}"})
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
    
    return questestinterop

def create_manifest_xml(assessment_ident, assessment_title):
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
    resource.set("href", "assessment.xml")

    # Convert the XML structure to a string
    manifest_xml = etree.tostring(imsmanifest, encoding="UTF-8", method="xml").decode("UTF-8")

    return manifest_xml

if __name__ == "__main__":
    main()
