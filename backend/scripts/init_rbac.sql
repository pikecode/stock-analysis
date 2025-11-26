-- ========================================
-- 初始化 RBAC 系统：角色和权限
-- ========================================

-- 1. 创建角色
INSERT INTO roles (name, description) VALUES
  ('admin', '系统管理员，拥有所有权限')
ON CONFLICT (name) DO NOTHING;

INSERT INTO roles (name, description) VALUES
  ('customer', '普通用户，可查看报表')
ON CONFLICT (name) DO NOTHING;

INSERT INTO roles (name, description) VALUES
  ('viewer', '访客，只能查看部分功能')
ON CONFLICT (name) DO NOTHING;

-- 2. 创建权限（使用 code 字段存储权限代码）
-- 导入权限
INSERT INTO permissions (code, name, description) VALUES
  ('import:upload', '上传导入文件', '允许上传导入文件')
ON CONFLICT (code) DO NOTHING;

INSERT INTO permissions (code, name, description) VALUES
  ('import:view', '查看导入记录', '允许查看导入记录')
ON CONFLICT (code) DO NOTHING;

INSERT INTO permissions (code, name, description) VALUES
  ('import:manage', '管理导入', '允许管理导入任务')
ON CONFLICT (code) DO NOTHING;

-- 报表权限
INSERT INTO permissions (code, name, description) VALUES
  ('report:view', '查看报表', '允许查看报表')
ON CONFLICT (code) DO NOTHING;

INSERT INTO permissions (code, name, description) VALUES
  ('report:export', '导出报表', '允许导出报表')
ON CONFLICT (code) DO NOTHING;

-- 查询权限
INSERT INTO permissions (code, name, description) VALUES
  ('stock:view', '查看股票', '允许查看股票信息')
ON CONFLICT (code) DO NOTHING;

INSERT INTO permissions (code, name, description) VALUES
  ('concept:view', '查看概念', '允许查看概念信息')
ON CONFLICT (code) DO NOTHING;

INSERT INTO permissions (code, name, description) VALUES
  ('ranking:view', '查看排名', '允许查看排名信息')
ON CONFLICT (code) DO NOTHING;

-- 3. 为 Admin 角色分配所有权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'admin'
ON CONFLICT DO NOTHING;

-- 4. 为 Customer 角色分配报表和查询权限
DELETE FROM role_permissions WHERE role_id = (SELECT id FROM roles WHERE name = 'customer');
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'customer'
  AND p.code IN ('report:view', 'report:export', 'stock:view', 'concept:view', 'ranking:view')
ON CONFLICT DO NOTHING;

-- 5. 为 Viewer 角色分配仅查询权限
DELETE FROM role_permissions WHERE role_id = (SELECT id FROM roles WHERE name = 'viewer');
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'viewer'
  AND p.code IN ('stock:view', 'concept:view', 'ranking:view')
ON CONFLICT DO NOTHING;

-- 6. 创建或更新测试用户（可选）
-- 注意：密码应该在代码中通过 get_password_hash 生成，这里只是示例
-- 实际密码应该通过 Python 的 password_context.hash() 生成

-- 创建 admin 用户（如果不存在）
INSERT INTO users (username, email, password_hash, status) VALUES
  ('admin', 'admin@example.com',
   '$2b$12$7V7jvqjVLvhp2aBiPL1eNu6N7x4vDWM3eP8q5zK5YjVz7z5p1m0Pu',
   'active')
ON CONFLICT (username) DO NOTHING;

-- 创建 customer 用户（如果不存在）
INSERT INTO users (username, email, password_hash, status) VALUES
  ('customer', 'customer@example.com',
   '$2b$12$7V7jvqjVLvhp2aBiPL1eNu6N7x4vDWM3eP8q5zK5YjVz7z5p1m0Pu',
   'active')
ON CONFLICT (username) DO NOTHING;

-- 7. 为用户分配角色
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.username = 'customer' AND r.name = 'customer'
ON CONFLICT DO NOTHING;

-- 8. 验证初始化结果
SELECT '=== Roles ===' as info;
SELECT id, name, description FROM roles ORDER BY name;

SELECT '=== Permissions ===' as info;
SELECT id, code, name, description FROM permissions ORDER BY code;

SELECT '=== Users and Roles ===' as info;
SELECT u.id, u.username, u.email, u.status,
       array_agg(r.name) as roles
FROM users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
GROUP BY u.id, u.username, u.email, u.status
ORDER BY u.username;

SELECT '=== Role Permissions ===' as info;
SELECT r.name as role, p.code as permission
FROM role_permissions rp
JOIN roles r ON rp.role_id = r.id
JOIN permissions p ON rp.permission_id = p.id
ORDER BY r.name, p.code;
