package se.fhir.education.fasad.provider;

import org.hl7.fhir.instance.model.api.IBaseConformance;
import org.hl7.fhir.r4.model.CapabilityStatement;
import org.hl7.fhir.r4.model.CapabilityStatement.CapabilityStatementRestResourceComponent;

import ca.uhn.fhir.interceptor.api.Hook;
import ca.uhn.fhir.interceptor.api.Interceptor;
import ca.uhn.fhir.interceptor.api.Pointcut;
import se.fhir.education.fasad.mapping.EncounterMapper;
import se.fhir.education.fasad.mapping.PatientMapper;

/**
 * HAPI genererar ett CapabilityStatement automatiskt utifrån våra resource providers.
 * Här lägger vi till sådant som HAPI inte kan veta: vilken IG och vilka profiler servern följer.
 */
@Interceptor
public class CapabilityStatementCustomizer {

  static final String KURS_IG = "http://example.org/fhir/education/kursig";

  @Hook(Pointcut.SERVER_CAPABILITY_STATEMENT_GENERATED)
  public void customize(IBaseConformance theCapabilityStatement) {
    CapabilityStatement cs = (CapabilityStatement) theCapabilityStatement;

    cs.setPublisher("FHIR-utbildning");
    // "Den här servern uppfyller kraven i ..." – se övning 6.2
    cs.addInstantiates(KURS_IG + "/CapabilityStatement/EducationServerCapabilities");
    cs.addImplementationGuide(KURS_IG + "/ImplementationGuide/fhir.education.kursig");

    for (CapabilityStatementRestResourceComponent resource : cs.getRestFirstRep().getResource()) {
      switch (resource.getType()) {
        case "Patient" -> resource.addSupportedProfile(PatientMapper.PROFIL);
        case "Encounter" -> resource.addSupportedProfile(EncounterMapper.PROFIL);
        default -> { }
      }
    }
  }
}
