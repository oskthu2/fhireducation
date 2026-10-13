package se.fhir.education.fasad;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.ServletRegistrationBean;
import org.springframework.context.annotation.Bean;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.api.EncodingEnum;
import ca.uhn.fhir.rest.server.RestfulServer;
import ca.uhn.fhir.rest.server.interceptor.ResponseHighlighterInterceptor;
import se.fhir.education.fasad.provider.CapabilityStatementCustomizer;
import se.fhir.education.fasad.provider.EncounterProvider;
import se.fhir.education.fasad.provider.PatientProvider;
import se.fhir.education.fasad.security.DemoAuthorizationInterceptor;

/**
 * Startar en FHIR-server (HAPI FHIR "Plain Server") på http://localhost:8080/fhir.
 * <p>
 * Servern har ingen egen databas – varje anrop översätts till ett anrop mot det befintliga
 * journalsystemet och svaret mappas till FHIR. Det kallas ofta för en FHIR-fasad.
 */
@SpringBootApplication
public class FasadApplication {

  public static void main(String[] args) {
    SpringApplication.run(FasadApplication.class, args);
  }

  @Bean
  public ServletRegistrationBean<RestfulServer> fhirServlet(
      PatientProvider patientProvider,
      EncounterProvider encounterProvider,
      @Value("${fasad.sakerhet.aktiv:false}") boolean sakerhetAktiv) {

    RestfulServer server = new RestfulServer(FhirContext.forR4Cached());
    server.setImplementationDescription("Kursens FHIR-fasad ovanpå ett befintligt journalsystem");

    // En "resource provider" per resurstyp som API:t ska erbjuda.
    server.setResourceProviders(patientProvider, encounterProvider);

    server.setDefaultResponseEncoding(EncodingEnum.JSON);
    server.setDefaultPrettyPrint(true);

    // Visar svaren som läsbar HTML när man surfar till API:t med en webbläsare.
    server.registerInterceptor(new ResponseHighlighterInterceptor());

    // Kompletterar det automatiskt genererade CapabilityStatement (GET /fhir/metadata).
    server.registerInterceptor(new CapabilityStatementCustomizer());

    if (sakerhetAktiv) {
      server.registerInterceptor(new DemoAuthorizationInterceptor());
    }

    ServletRegistrationBean<RestfulServer> registration = new ServletRegistrationBean<>(server, "/fhir/*");
    registration.setLoadOnStartup(1);
    return registration;
  }
}
