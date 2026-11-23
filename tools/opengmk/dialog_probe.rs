//! Controlled real-window probe. No game executable, resources or GML required.
mod message_dialog;

fn main() -> std::io::Result<()> {
    for (expected, instruction) in [
        (1, "Select Alpha with the mouse."),
        (2, "Select Beta with the mouse."),
        (3, "Select Gamma with the keyboard (Tab then Enter)."),
        (0, "Press Escape. No game frame may advance while this dialog is open."),
    ] {
        println!("BEFORE expected={expected}");
        let started = std::time::Instant::now();
        let actual = message_dialog::show(0, instruction, ["Alpha", "Beta", "Gamma"])?;
        println!("AFTER expected={expected} actual={actual} modal_ms={}", started.elapsed().as_millis());
        assert_eq!(actual, expected);
    }
    println!("DIALOG_PROBE_PASS");
    Ok(())
}
