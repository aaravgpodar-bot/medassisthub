document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".flash").forEach((item) => {
        setTimeout(() => item.remove(), 5000);
    });

    const accountType = document.querySelector("#account_type");
    const updateAccountFields = () => {
        if (!accountType) return;
        const isPatient = accountType.value === "patient";
        document.querySelectorAll(".staff-field").forEach((field) => {
            field.hidden = isPatient;
        });
        document.querySelectorAll(".patient-field").forEach((field) => {
            field.hidden = !isPatient;
        });
    };

    if (accountType) {
        updateAccountFields();
        accountType.addEventListener("change", updateAccountFields);
    }
});
