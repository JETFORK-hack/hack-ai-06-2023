import jetforkLogo from '../../logo_white_transporent.png';
import { Layout, Menu, Breadcrumb, theme } from 'antd';
import { basePath } from '../../providers/env';


const items = [
    {
        key: '1',
        label: 'Отправить на проверку',
    },
    {
        key: '2',
        label: 'qwe',
    },
]


export default function Header() {
    const {
        token: { colorBgContainer },
    } = theme.useToken();

    return (
        <Layout className="layout">
            <Layout.Header style={{ display: 'flex', alignItems: 'center' }}>
                <img src={jetforkLogo} style={{ height: '100%', paddingRight: 50 }} />
                <Menu theme="dark" mode="horizontal" items={items}
                    defaultSelectedKeys={['1']} />
            </Layout.Header>
            <Layout.Content style={{ padding: '0 50px', height: '100%' }}>
                <Breadcrumb style={{ margin: '16px 0' }}>
                    <Breadcrumb.Item>Home</Breadcrumb.Item>
                    <Breadcrumb.Item>List</Breadcrumb.Item>
                    <Breadcrumb.Item>App</Breadcrumb.Item>
                </Breadcrumb>
                <div className="site-layout-content" style={{ background: colorBgContainer }}>
                    Content {basePath}
                </div>
            </Layout.Content>
            <Layout.Footer style={{ textAlign: 'center' }}>Ant Design ©2023 Created by Ant UED</Layout.Footer>
        </Layout>
    )
}
