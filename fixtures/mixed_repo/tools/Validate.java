// Residue file (Java) — no frozen extractor, routes to the model fallback (TASK-010).
// A second residue language so mixed_repo exercises more than one un-onboarded language.
package tools;

public class Validate {
    public static boolean handlerIdInRange(int handlerId) {
        return handlerId >= 0 && handlerId < 8;
    }

    public static void main(String[] args) {
        System.out.println(handlerIdInRange(3));
    }
}
