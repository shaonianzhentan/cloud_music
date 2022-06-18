import React from 'react';
import { Col, Row, Slider, Dropdown, Space, Menu, } from 'antd'
import { PlayCircleOutlined, StepBackwardOutlined, StepForwardOutlined, CustomerServiceOutlined, DownOutlined } from '@ant-design/icons';
import styles from './PlayControl.less';

const menu = (
  <Menu
    items={[
      {
        key: '1',
        label: (
          <a rel="noopener noreferrer" href="#">
            网页浏览器
          </a>
        ),
      },
      {
        key: '2',
        label: (
          <a rel="noopener noreferrer" href="#">
            MPD
          </a>
        ),
      },
      {
        key: '3',
        label: (
          <a rel="noopener noreferrer" href="#">
            Windows应用
          </a>
        ),
      },
    ]}
  />
);

export default function PlayControl() {
  return (
    <Row justify="space-around" align="middle">
      <Col flex="180px">
        <StepBackwardOutlined style={{ fontSize: '30px', color: '#03a9f4' }} />
        <PlayCircleOutlined style={{ fontSize: '35px', color: '#03a9f4', margin: '0 15px' }} />
        <StepForwardOutlined style={{ fontSize: '30px', color: '#03a9f4' }} />
      </Col>
      <Col flex="auto">
        <Slider defaultValue={37} />
      </Col>
      <Col flex="150px">
        <Slider defaultValue={30} />
      </Col>
      <Col style={{ textAlign: 'right' }}>
        <Dropdown overlay={menu} placement="topRight">
          <Space style={{ marginLeft: '25px' }}>
            音乐播放器
            <DownOutlined />
          </Space>
        </Dropdown>
      </Col>
    </Row>
  );
}