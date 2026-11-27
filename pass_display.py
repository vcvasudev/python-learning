import subprocess as sp


def get_saved_profiles():
    """Return a set of all Wi-Fi profile names saved on this PC."""
    output = sp.check_output("netsh wlan show profiles", shell=True).decode(
        "utf-8", errors="ignore"
    )
    return {
        line.split(":", 1)[1].strip()
        for line in output.splitlines()
        if "All User Profile" in line
    }


def scan_all_wifi_networks():
    saved_profiles = get_saved_profiles()

    # Scan all nearby Wi-Fi networks currently in range
    scan_output = sp.check_output(
        "netsh wlan show networks mode=bssid", shell=True
    ).decode("utf-8", errors="ignore")

    networks = []
    current = {}

    for line in scan_output.splitlines():
        line = line.strip()
        # Match "SSID 1 : NetworkName" (ignore "BSSID 1 : ...")
        if line.startswith("SSID ") and ":" in line:
            if current:
                networks.append(current)
            ssid = line.split(":", 1)[1].strip() or "<Hidden Network>"
            current = {"ssid": ssid, "auth": "Unknown", "signal": "N/A"}
        elif line.startswith("Authentication") and current:
            current["auth"] = line.split(":", 1)[1].strip()
        elif line.startswith("Signal") and current and current["signal"] == "N/A":
            current["signal"] = line.split(":", 1)[1].strip()

    if current:
        networks.append(current)

    if not networks:
        print("No nearby Wi-Fi networks found (make sure Wi-Fi is turned ON).")
        return

    print(f"\n{'No.':<4} {'Wi-Fi Name (SSID)':<28} {'Signal':<8} {'Security':<18} {'Status'}")
    print("-" * 75)
    for i, net in enumerate(networks, 1):
        status = "Saved" if net["ssid"] in saved_profiles else "Not Saved"
        print(
            f"{i:<4} {net['ssid']:<28} {net['signal']:<8} {net['auth']:<18} {status}"
        )

    # Interactive lookup loop
    while True:
        choice = input("\nChoose a network number to check details/password (0 to exit): ").strip()

        if choice == "0":
            print("Exiting...")
            break

        if not choice.isdigit() or not (1 <= int(choice) <= len(networks)):
            print(f"Enter a valid number between 1 and {len(networks)} (or 0 to exit).")
            continue

        selected = networks[int(choice) - 1]
        ssid = selected["ssid"]

        if ssid in saved_profiles:
            details = sp.check_output(
                f'netsh wlan show profile name="{ssid}" key=clear', shell=True
            ).decode("utf-8", errors="ignore")

            for line in details.splitlines():
                if "Key Content" in line:
                    pwd = line.split(":", 1)[1].strip()
                    print(f"Saved Password for '{ssid}': {pwd}")
                    break
            else:
                print(f"'{ssid}' is saved, but has no password (Open network).")
        else:
            print(
                f"'{ssid}' is NOT saved on this computer (Signal: {selected['signal']}, Security: {selected['auth']})."
            )


if __name__ == "__main__":
    scan_all_wifi_networks()
