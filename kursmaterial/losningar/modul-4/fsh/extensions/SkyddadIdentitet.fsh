// Övning 3.4: En egen, enkel extension.
// OBS! Fiktiv extension för utbildningen. Diskutera: hade meta.security varit ett bättre val?
Extension: SkyddadIdentitet
Id: SkyddadIdentitet
Title: "Skyddad identitet"
Description: "Anger om patienten har skyddade personuppgifter (t.ex. sekretessmarkering eller skyddad folkbokföring)."
Context: Patient

* value[x] 1..1
* value[x] only boolean
