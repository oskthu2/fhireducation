// Övning 4: Egna invarianter (constraints) skrivna i FHIRPath.
// Ett invariant-uttryck ska returnera true för att instansen ska vara giltig.

Invariant: edu-pat-1
Description: "Ett personnummer ska bestå av exakt 12 siffror (ÅÅÅÅMMDDNNNN)."
Expression: "identifier.where(system = 'http://electronichealth.se/identifier/personnummer').all(value.matches('^[0-9]{12}$'))"
Severity: #error

Invariant: edu-pat-2
Description: "Födelsedatum får inte ligga i framtiden."
Expression: "birthDate.empty() or birthDate <= today()"
Severity: #error

Invariant: edu-enc-1
Description: "En avslutad vårdkontakt (status = finished) ska ha en sluttid (period.end)."
Expression: "status = 'finished' implies period.end.exists()"
Severity: #error

Invariant: edu-enc-2
Description: "Sluttiden bör inte ligga före starttiden."
Expression: "period.end.empty() or period.start <= period.end"
Severity: #warning
