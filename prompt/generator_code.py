import xml.etree.ElementTree as ET
from xml.dom import minidom


def ask_list(prompt):
    print(f"{prompt} (comma-separated)")
    return [item.strip() for item in input("> ").split(",") if item.strip()]


def create_element_with_list(tag, items, item_tag):
    parent = ET.Element(tag)
    for item in items:
        child = ET.SubElement(parent, item_tag)
        child.text = item
    return parent


def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    return minidom.parseString(rough_string).toprettyxml(indent="  ")


def main():
    root = ET.Element("CodingTaskPrompt")

    # Task Summary
    summary = input("📝 Task Summary (What should the code do?):\n> ")
    ET.SubElement(root, "TaskSummary").text = summary

    # Requirements and Constraints
    reqs = ET.SubElement(root, "RequirementsAndConstraints")
    ET.SubElement(reqs, "Language").text = input("🔧 Programming Language:\n> ")
    ET.SubElement(reqs, "DesignPattern").text = input("🎯 Design Pattern (optional):\n> ")

    must_support = ask_list("✅ Must support features")
    reqs.append(create_element_with_list("MustSupport", must_support, "Feature"))

    avoid = ask_list("🚫 Avoid (anti-patterns)")
    reqs.append(create_element_with_list("Avoid", avoid, "AntiPattern"))

    ET.SubElement(reqs, "TargetPlatform").text = input("💻 Target Platform or Environment:\n> ")

    # I/O Examples
    io = ET.SubElement(root, "IO")
    ET.SubElement(ET.SubElement(io, "Input"), "Example").text = input("📥 Input Example (JSON format):\n> ")
    ET.SubElement(ET.SubElement(io, "Output"), "Example").text = input("📤 Output Example (JSON format):\n> ")

    # Special Considerations
    considerations = ask_list("⚠️ Special Considerations (e.g., performance, edge cases)")
    root.append(create_element_with_list("SpecialConsiderations", considerations, "Consideration"))

    # Success Criteria
    criteria = ask_list("🎯 Success Criteria")
    root.append(create_element_with_list("SuccessCriteria", criteria, "Criterion"))

    # Optional Extras
    extras = ask_list("📚 Optional Extras (optional, skip if none)")
    if extras:
        root.append(create_element_with_list("OptionalExtras", extras, "Extra"))

    # Output the final XML
    xml_output = prettify(root)
    print("\n📄 Generated XML Prompt Template:\n")
    print(xml_output)

    # Optionally write to file
    save = input("💾 Save to file? (y/n):\n> ").strip().lower()
    if save == 'y':
        filename = input("Enter filename (e.g., prompt_gen.xml):\n> ")
        with open(filename, "w") as f:
            f.write(xml_output)
        print(f"✅ Saved to {filename}")


if __name__ == "__main__":
    main()
