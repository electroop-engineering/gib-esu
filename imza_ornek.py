import xmlsec
from lxml import etree

CERTIFICATE_PATH = "./resources/certificates/chain.pem"
PRIVATE_KEY_PATH = "./resources/certificates/private_key_rsa.pem"

##########
# SIGN
##########

xml_path = "./resources/data/xml_data_to_be_signed.xml"
template = etree.parse(xml_path).getroot()

sign_ctx = xmlsec.SignatureContext()

key = xmlsec.Key.from_file(PRIVATE_KEY_PATH, xmlsec.constants.KeyDataFormatPem)

sign_ctx.key = key

signature_node = xmlsec.tree.find_node(template, xmlsec.constants.NodeSignature)

sign_ctx.sign(signature_node)  # type: ignore

print(etree.tostring(template))

##########
# VERIFY
##########

root = etree.XML(etree.tostring(template))

signature_node = xmlsec.tree.find_node(root, xmlsec.constants.NodeSignature)

if signature_node is None:
    raise Exception("Signature element not found in XML.")

key.load_cert_from_file(CERTIFICATE_PATH, xmlsec.constants.KeyDataFormatPem)

ctx = xmlsec.SignatureContext()
ctx.key = key

try:
    ctx.verify(signature_node)
    print("Signature is valid.")
except xmlsec.Error as e:
    print(f"Signature validation failed: {e}")
