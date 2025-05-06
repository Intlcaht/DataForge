# ✅ ITGC Controls Matrix

| Control ID | Control Area       | Control Description                                          | Control Owner       | Frequency    | Evidence/Artifact                          | System Scope                                                                 |
|------------|--------------------|--------------------------------------------------------------|---------------------|--------------|--------------------------------------------|-------------------------------------------------------------------------------|
| **AC-01**  | Access Control      | All users have unique IDs and are authenticated via MFA      | DevOps Lead         | Continuous   | User access logs, MFA configs              | Internal portals, databases (e.g., pgAdmin), SSH, Git, cloud consoles, CI/CD |
| **AC-02**  | Access Control      | Access permissions reviewed quarterly                        | Security Manager    | Quarterly    | Access review reports                      | Admin panels, database roles, IAM, CI/CD, Git repos                          |
| **AC-03**  | Access Control      | User access removed immediately upon termination             | HR / IT             | As needed    | Termination checklist, deactivation logs   | All internal systems: portals, DBs, SSH, Git, CI/CD                          |
| **CM-01**  | Change Management   | All changes require documented approval before implementation| Tech Lead           | Continuous   | Approved change requests, Git PRs          | GitHub/GitLab, CI/CD, Infra-as-Code                                          |
| **CM-02**  | Change Management   | All code changes are reviewed and tested before deployment   | Developers          | Continuous   | Code review history, test reports          | Source repositories, CI/CD pipelines                                         |
| **CM-03**  | Change Management   | Emergency changes are logged and approved retrospectively    | Engineering Manager | As needed    | Emergency change logs                      | Infrastructure, codebase, production systems                                 |
| **OP-01**  | IT Operations       | Daily automated backups for critical systems                 | SysAdmin            | Daily        | Backup logs, monitoring dashboards         | Databases, application servers, storage                                      |
| **OP-02**  | IT Operations       | Monthly backup restoration test                              | SysAdmin            | Monthly      | Restoration reports, test logs             | Databases, infrastructure                                                    |
| **OP-03**  | IT Operations       | Critical jobs are monitored for failures                     | DevOps Engineer     | Continuous   | Alerting system logs                       | Cron jobs, backup systems, CI/CD pipelines                                   |
| **SM-01**  | Security Monitoring | All privileged actions are logged                            | Backend Lead        | Continuous   | Audit log entries                          | Admin panels, databases, cloud IAM, SSH, Kubernetes                          |
| **SM-02**  | Security Monitoring | Logs are retained for 90 days minimum                        | Security Engineer   | Continuous   | Log storage policy, archived logs          | Audit systems, server logs, app logs                                         |
| **SM-03**  | Security Monitoring | Unusual login attempts are flagged and reviewed              | Security Analyst    | Weekly       | Alert reports, investigation outcomes      | Admin portals, DB consoles, SSH, cloud consoles                              |
| **SDLC-01**| SDLC Controls       | Secure coding standards are enforced                         | Development Lead    | Continuous   | Dev checklist, secure code policy          | Source code management, documentation                                        |
| **SDLC-02**| SDLC Controls       | Static code scans are run on all builds                      | CI/CD Engineer      | Continuous   | CI pipeline logs, scan reports             | GitHub/GitLab pipelines, SAST tools                                          |
| **SDLC-03**| SDLC Controls       | Developers receive annual security training                  | HR / Security Lead  | Annually     | Training attendance records                | Development team                                                             |
| **PHY-01** | Physical Security   | Server room access restricted to authorized personnel        | IT Manager          | Continuous   | Access logs, badge system reports          | Data center / office environment                                             |
| **PHY-02** | Physical Security   | Environmental systems (power, fire, temperature) in place    | Facilities Manager  | Continuous   | Maintenance logs, inspection reports       | Server rooms, office facilities                                              |


# 📌 Systems and Their ITGC Spec

| System         | Matrix Cod               | Spec                                                        |
|--------------------|-----------------------------------|-----------------------------------------------------------------|
| Portals & Dashboards| AC-01, AC-02, AC-03, SM-01        | Internal CMS, analytics dashboards, approval workflows, Twenty, Smallbads        |
| Databases           | AC-01, AC-02, AC-03, SM-01, SM-03 | PostgreSQL, MySQL, MongoDB, Neo4j, Redis — including direct shell access |
| Cloud Platforms     | AC-01, AC-02, AC-03, SM-01, SM-03 | GCP, Terraform and resource management                     |
| Infrastructure      | AC-01, AC-03, SM-01               | Kubernetes dashboard, Docker hosts, Ansible, Terraform         |
| Dev Tools           | AC-01, AC-02, AC-03               | GitHub, Jenkins, CI/CD pipelines                |
| Access Layers       | AC-01, AC-03, SM-03               | SSH, Mesh                                      |
