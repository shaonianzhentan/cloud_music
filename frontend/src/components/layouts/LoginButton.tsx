import { createRef, useState } from 'react'
import { Button, Checkbox, Form, Input, Modal, message } from 'antd'
import { UserOutlined, LockOutlined, OrderedListOutlined, BarsOutlined, HomeOutlined, LoginOutlined } from '@ant-design/icons';
import styles from './LoginButton.less'
import { ha } from '../../http/cloudMusic'

export default function Page() {

    const [isModalVisible, setIsModalVisible] = useState(false);

    const showModal = () => {
        setIsModalVisible(true);
    };

    const handleOk = () => {
        setIsModalVisible(false);
    };

    const handleCancel = () => {
        setIsModalVisible(false);
    };

    const onFinish = async (values: any) => {
        console.log('Success:', values);
        const username: string = values['username']
        const password: string = values['password']
        let url = `/login`
        if (username.includes('@')) {
            url += `?email=`
        } else {
            url += `/cellphone?phone=`
        }
        const res = await ha.neteaseCloudMusic(url + `${username}&password=${password}`)
        if (res.data.code == 200) {
            message.success(`【${res.data.profile.nickname}】登录成功`)
            setIsModalVisible(false);
        } else {
            message.error('账户或密码错误')
        }
    };

    const onFinishFailed = (errorInfo: any) => {
        console.log('Failed:', errorInfo);
    };

    return (
        <>
            <Button key="1" shape="circle" type="text" onClick={showModal}>
                <LoginOutlined style={{ color: 'white' }} />
            </Button>
            <Modal className={styles.modal} title="云音乐" width={400} visible={isModalVisible} onOk={handleOk} onCancel={handleCancel}>
                <Form
                    name="basic"
                    labelCol={{ span: 0 }}
                    wrapperCol={{ span: 24 }}
                    initialValues={{ remember: true }}
                    onFinish={onFinish}
                    onFinishFailed={onFinishFailed}
                    autoComplete="off"
                >
                    <Form.Item
                        name="username"
                        rules={[{ required: true, message: '这个要填' }]}
                    >
                        <Input prefix={<UserOutlined className="site-form-item-icon" />} placeholder="邮箱/手机号" />
                    </Form.Item>
                    <Form.Item
                        name="password"
                        rules={[{ required: true, message: '这个也要填' }]}
                    >
                        <Input
                            prefix={<LockOutlined className="site-form-item-icon" />}
                            type="password"
                            placeholder="网易云音乐密码"
                        />
                    </Form.Item>
                    <Form.Item wrapperCol={{ offset: 0, span: 24 }}>
                        <Button type="primary" htmlType="submit" block>
                            点击开始登录咯
                        </Button>
                    </Form.Item>
                </Form>
                <p>登录后会将cookie保存在HomeAssistant存储目录之中</p>
                <p>为防止你的账号密码泄露，建议自行部署API接口服务</p>
                <p>如果你不听，那就当我没说😂</p>
            </Modal>
        </>
    )
}