package se.fhir.education.fasad.security;

import java.util.List;
import java.util.Map;
import java.util.Set;

import org.hl7.fhir.r4.model.Encounter;
import org.hl7.fhir.r4.model.Patient;

import ca.uhn.fhir.rest.api.RestOperationTypeEnum;
import ca.uhn.fhir.rest.api.server.RequestDetails;
import ca.uhn.fhir.rest.server.exceptions.AuthenticationException;
import ca.uhn.fhir.rest.server.interceptor.auth.AuthorizationInterceptor;
import ca.uhn.fhir.rest.server.interceptor.auth.IAuthRule;
import ca.uhn.fhir.rest.server.interceptor.auth.RuleBuilder;

/**
 * FÖRENKLAT EXEMPEL – ANVÄND INTE I PRODUKTION.
 * <p>
 * Visar principen för scope-baserad behörighet enligt SMART on FHIR / OAuth 2.0:
 * klienten skickar en access token, servern tar fram tokenens scopes och tillåter bara
 * de operationer som scopen ger rätt till.
 * <p>
 * I en riktig lösning utfärdas token av en auktorisationsserver (t.ex. med SMART Backend Services
 * eller IHE IUA) och fasaden validerar en JWT: signatur, utfärdare (iss), mottagare (aud) och
 * giltighetstid (exp) – i stället för att slå upp den i en hårdkodad lista som här.
 */
public class DemoAuthorizationInterceptor extends AuthorizationInterceptor {

  /** Påhittade tokens och deras scopes (SMART v2-syntax: system/Resurs.rs = read + search). */
  private static final Map<String, Set<String>> DEMO_TOKENS = Map.of(
      "demo-token-patient", Set.of("system/Patient.rs"),
      "demo-token-alla", Set.of("system/Patient.rs", "system/Encounter.rs"));

  @Override
  public List<IAuthRule> buildRuleList(RequestDetails request) {
    RuleBuilder rules = new RuleBuilder();

    // CapabilityStatement ska alltid vara åtkomligt (capability discovery).
    rules.allow("metadata").metadata();
    if (request.getRestOperationType() == RestOperationTypeEnum.METADATA) {
      return rules.build();
    }

    String header = request.getHeader("Authorization");
    if (header == null || !header.startsWith("Bearer ")) {
      throw new AuthenticationException("Saknar access token (Authorization: Bearer ...)");
    }
    Set<String> scopes = DEMO_TOKENS.get(header.substring("Bearer ".length()).trim());
    if (scopes == null) {
      throw new AuthenticationException("Ogiltig access token");
    }

    if (scopes.contains("system/Patient.rs")) {
      rules.allow("Läsa patienter").read().resourcesOfType(Patient.class).withAnyId();
    }
    if (scopes.contains("system/Encounter.rs")) {
      rules.allow("Läsa vårdkontakter").read().resourcesOfType(Encounter.class).withAnyId();
    }
    rules.denyAll("Token saknar scope för den här operationen");
    return rules.build();
  }
}
