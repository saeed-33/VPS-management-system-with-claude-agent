-- Replace the one-size-fits-all command fingerprint policy with practical
-- policies that match the stability and diagnostic value of each command.
-- The migration is idempotent for the built-in command catalog.

BEGIN;

UPDATE monitor_commands
SET
    fingerprint_strategy = CASE name
        WHEN 'uptime' THEN 'status_only'
        WHEN 'hostname' THEN 'full_output'
        WHEN 'operating_system' THEN 'full_output'
        WHEN 'current_time' THEN 'exclude_output'
        WHEN 'cpu_info' THEN 'canonical_lines'
        WHEN 'memory_usage' THEN 'status_only'
        WHEN 'disk_usage' THEN 'canonical_lines'
        WHEN 'disk_inodes' THEN 'canonical_lines'
        WHEN 'load_average' THEN 'status_only'
        WHEN 'running_processes' THEN 'status_only'
        WHEN 'failed_services' THEN 'error_signature'
        WHEN 'listening_ports' THEN 'canonical_lines'
        WHEN 'recent_errors' THEN 'error_signature'
        ELSE fingerprint_strategy
    END,
    fingerprint_config = CASE name
        WHEN 'failed_services' THEN '{"remove_timestamps": true}'::json
        WHEN 'recent_errors' THEN '{"remove_timestamps": true}'::json
        ELSE '{}'::json
    END,
    updated_at = NOW()
WHERE name IN (
    'uptime',
    'hostname',
    'operating_system',
    'current_time',
    'cpu_info',
    'memory_usage',
    'disk_usage',
    'disk_inodes',
    'load_average',
    'running_processes',
    'failed_services',
    'listening_ports',
    'recent_errors'
);

COMMIT;
