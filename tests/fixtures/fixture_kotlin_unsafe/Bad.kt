// TODO: drop the not-null assertions
package demo

fun bad(name: String?) {
    println("hello $name")
    val length = name!!.length
    Runtime.getRuntime().exec("ls -la")
    try {
        // op
    } catch (e: Exception) {
    }
    TODO("not implemented")
}
