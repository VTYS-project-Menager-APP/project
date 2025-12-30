-- Smart Transport Alarm System Migration
-- Adds support for multiple routes, origin/destination, and smart alarm features

-- 1. Create new table for alarm selected routes
CREATE TABLE IF NOT EXISTS alarm_selected_routes (
    id SERIAL PRIMARY KEY,
    alarm_id INTEGER NOT NULL REFERENCES user_transport_alarms(id) ON DELETE CASCADE,
    hat_kodu VARCHAR(50) NOT NULL,
    hat_adi VARCHAR(255),
    tahmini_sure INTEGER,
    priority INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Add new columns to user_transport_alarms table
ALTER TABLE user_transport_alarms 
ADD COLUMN IF NOT EXISTS origin_location VARCHAR(255),
ADD COLUMN IF NOT EXISTS destination_location VARCHAR(255),
ADD COLUMN IF NOT EXISTS origin_durak_kodu VARCHAR(50),
ADD COLUMN IF NOT EXISTS destination_durak_kodu VARCHAR(50),
ADD COLUMN IF NOT EXISTS target_arrival_time VARCHAR(5),
ADD COLUMN IF NOT EXISTS alarm_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_triggered TIMESTAMP;

-- 3. Modify existing columns to be nullable for backward compatibility
ALTER TABLE user_transport_alarms 
ALTER COLUMN route_id DROP NOT NULL;

-- 4. Update notification_minutes_before default value
ALTER TABLE user_transport_alarms 
ALTER COLUMN notification_minutes_before SET DEFAULT 5;

-- 5. Update travel_time_to_stop default value
ALTER TABLE user_transport_alarms 
ALTER COLUMN travel_time_to_stop SET DEFAULT 10;

-- 6. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_alarm_selected_routes_alarm_id ON alarm_selected_routes(alarm_id);
CREATE INDEX IF NOT EXISTS idx_alarm_selected_routes_hat_kodu ON alarm_selected_routes(hat_kodu);
CREATE INDEX IF NOT EXISTS idx_user_transport_alarms_origin_durak ON user_transport_alarms(origin_durak_kodu);
CREATE INDEX IF NOT EXISTS idx_user_transport_alarms_dest_durak ON user_transport_alarms(destination_durak_kodu);
CREATE INDEX IF NOT EXISTS idx_user_transport_alarms_target_time ON user_transport_alarms(target_arrival_time);

-- 7. Add comments for documentation
COMMENT ON TABLE alarm_selected_routes IS 'Stores multiple bus routes that can trigger a single alarm';
COMMENT ON COLUMN user_transport_alarms.origin_location IS 'Starting location (address or stop name)';
COMMENT ON COLUMN user_transport_alarms.destination_location IS 'Destination location (work address)';
COMMENT ON COLUMN user_transport_alarms.origin_durak_kodu IS 'IBB API stop code for origin';
COMMENT ON COLUMN user_transport_alarms.destination_durak_kodu IS 'IBB API stop code for destination';
COMMENT ON COLUMN user_transport_alarms.target_arrival_time IS 'Time user needs to arrive at destination (HH:MM)';
COMMENT ON COLUMN user_transport_alarms.alarm_name IS 'User-friendly alarm name (e.g., "Morning Commute")';
COMMENT ON COLUMN user_transport_alarms.last_triggered IS 'Last time this alarm was triggered';

