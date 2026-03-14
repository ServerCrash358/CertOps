package certops

deny[msg] {
    input.action == "restart_all_pods"
    msg = "Restarting all pods is unsafe"
}

deny[msg] {
    input.cpu > 90
    input.action == "increase_load"
    msg = "Cannot increase load when CPU is already high"
}

allow {
    not deny[_]
}