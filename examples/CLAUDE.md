# Example: project-specific criticality

Add a section like this to a project's CLAUDE.md. Use this exact heading: the divide-et-impera skill looks for it. Everything listed is treated as critical, in addition to the general criticality test in the skill.

## Critical in this project

- Database migrations under `db/migrations/`: production data, cannot be rolled back automatically.
- Anything under `src/billing/`: money calculations; rounding errors are silent.
- `config/production.yaml`: affects every deployment.
- The public REST API schema in `api/openapi.yaml`: external clients depend on it.

<!--
More examples by project type:

Hackintosh / firmware:
- OpenCore config.plist, ACPI SSDTs, kexts, boot-args, SIP/AMFI settings (a mistake can leave the machine unbootable).

Game:
- Save-file format and its migration code (players lose progress).

Mobile app:
- Push-notification and in-app purchase code (outward-facing, store review).
-->
