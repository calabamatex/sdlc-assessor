import java.io.IOException;

public class Bad {
    // TODO: replace Runtime.exec with ProcessBuilder
    public static void main(String[] args) {
        System.out.println("starting");
        try {
            Runtime.getRuntime().exec("ls -la");
        } catch (IOException e) {}
        try {
            Class.forName("com.foo.Bar");
        } catch (Exception e) {
            e.printStackTrace();
        }
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {}
    }
}
