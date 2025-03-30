-- 予約確定時のポイント支払いルールを追加
INSERT INTO pnt_details_rules 
(rule_name, rule_description, transaction_type, point_type, point_value, is_addition) 
VALUES 
('reservation_payment', '予約確定時のポイント支払い', 'reservation_payment', 'regular', 0, false) 
ON CONFLICT (rule_name) DO NOTHING;
