def ask(question, default=None, multiline=False):
    print(f"{question}")
    if default:
        print(f"(Press Enter to use default: {default})")
    if multiline:
        print("(Enter multiple lines. End with an empty line.)")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        return "\n".join(lines) if lines else default
    else:
        response = input("> ").strip()
        return response if response else default


def ask_list(question):
    print(f"{question} (comma-separated)")
    return [item.strip() for item in input("> ").split(",") if item.strip()]


def generate_prompt():
    lines = []

    lines.append("# 📘 System Specification Prompt")
    lines.append("")

    # Overview
    lines.append("## 1. Overview")
    lines.append(f"- **App Name**: {ask('What is the name of the system/app?')}")
    lines.append(f"- **Type**: {ask('What type of system/app is this? (e.g., mobile app, SaaS, marketplace)')}")
    lines.append(f"- **Purpose**: {ask('What problem does it solve?')}")
    lines.append(f"- **Target Audience**: {ask('Who are the target users or customers?')}")
    lines.append("")

    # Core Features
    lines.append("## 2. Core Features")
    features = ask_list("List the core features")
    for f in features:
        lines.append(f"- [ ] {f} — *(Must-have/Nice-to-have)*")
    lines.append("")

    # User Roles
    lines.append("## 3. User Roles")
    roles = ask_list("List the user roles")
    for role in roles:
        lines.append(f"- **{role}**: {ask(f'What can the {role} do?')}")
    lines.append("")

    # User Journeys
    lines.append("## 4. User Journeys")
    for role in roles:
        lines.append(f"### {role} Journey")
        journey = ask(f"Describe a typical journey for {role}:", multiline=True)
        lines.append(journey)
    lines.append("")

    # Architecture
    lines.append("## 5. System Architecture")
    lines.append(f"- **Architecture Style**: {ask('What architecture style? (e.g., Microservices, Monolith, Serverless)')}")
    lines.append(f"- **Backend**: {ask('What backend language/framework will be used?')}")
    lines.append(f"- **Frontend**: {ask('What frontend tech stack will be used?')}")
    lines.append(f"- **Database/Storage**: {ask('What database or storage system will be used?')}")
    lines.append("")

    # API & Integrations
    lines.append("## 6. API & Integrations")
    integrations = ask_list("List external services to integrate with")
    for integration in integrations:
        lines.append(f"- {integration}")
    lines.append(f"- **Data Format**: {ask('What is the expected data format? (e.g., JSON, GraphQL)')}")
    lines.append("")

    # Security
    lines.append("## 7. Security & Authentication")
    lines.append(f"- **Authentication**: {ask('What type of authentication? (e.g., JWT, OAuth2)')}")
    lines.append(f"- **Authorization**: {ask('Describe access control methods (e.g., RBAC)')}")
    lines.append("")

    # Scalability
    lines.append("## 8. Scalability & Performance")
    lines.append(f"- **Traffic Expectations**: {ask('Estimated traffic or users?')}")
    lines.append(f"- **Performance Strategies**: {ask('How will it be optimized? (e.g., Caching, CDNs)')}")
    lines.append("")

    # Deployment
    lines.append("## 9. Deployment Strategy")
    lines.append(f"- **CI/CD Tools**: {ask('What CI/CD tools or pipeline will be used?')}")
    lines.append(f"- **Cloud Provider**: {ask('Which cloud provider or host?')}")
    lines.append(f"- **Environments**: {ask('List environments (e.g., dev, staging, prod)')}")
    lines.append("")

    # Monitoring
    lines.append("## 10. Monitoring & Maintenance")
    lines.append(f"- **Monitoring Tools**: {ask('What monitoring or logging tools will be used?')}")
    lines.append(f"- **Health Checks**: {ask('Describe how the system will be monitored for uptime.')}")
    lines.append("")

    # Compliance
    lines.append("## 11. Legal & Compliance")
    lines.append(f"- **Regulations**: {ask('Any legal requirements like GDPR, HIPAA, etc?')}")
    lines.append(f"- **Policies**: {ask('What policies will be provided (e.g., ToS, Privacy Policy)?')}")
    lines.append("")

    # Timeline
    lines.append("## 12. Timeline & Milestones")
    lines.append(f"- **Development Timeline**: {ask('Estimated total timeline?')}")
    lines.append(f"- **MVP Scope**: {ask('What features will be included in the MVP?')}")
    lines.append(f"- **Phases/Sprints**: {ask('How will the project be phased or sprinted?')}")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    markdown_prompt = generate_prompt()
    print("\n📝 Generated Markdown Prompt:\n")
    print(markdown_prompt)

    if input("\n💾 Save to file? (y/n): ").lower() == "y":
        file_name = input("Filename (e.g., spec_gen.md): ")
        with open(file_name, "w") as f:
            f.write(markdown_prompt)
        print(f"✅ Saved to {file_name}")
