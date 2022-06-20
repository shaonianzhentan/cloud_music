import React, { useState, useEffect } from 'react';
import { Col, Row, Slider, Dropdown, Space, Menu, } from 'antd'
import { PlayCircleOutlined, StepBackwardOutlined, StepForwardOutlined, PauseCircleOutlined, DownOutlined } from '@ant-design/icons';
import styles from './PlayControl.less';
import { ha } from '../../http/cloudMusic'
import _ from 'lodash'

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

ha.audio.ontimeupdate = _.debounce(() => {
  console.log(ha.audio.currentTime)
  // 更新
  ha.cloudMusicServer({
    action: 'update',
    media_position: ha.audio.currentTime,
    media_duration: ha.audio.duration,
    volume_level: ha.audio.volume,
    is_volume_muted: ha.audio.muted
  })
}, 1000)

ha.audio.onended = () => {
  console.log('end')
}

// 订阅事件
ha.subscribeEvents(({ data }: any) => {
  console.log(data)
  const { audio } = ha
  // 加载音乐
  if ('play_media' in data) {
    audio.src = data.play_media
    audio.play()
    return
  }
  // 操作
  if ('action' in data) {
    switch (data.action) {
      case 'play':
        if (audio.paused) audio.play()
        break;
      case 'pause':
        if (!audio.paused) audio.pause()
        break;
    }
  }
})

// 解决音乐播放问题
document.onmousemove = () => {
  ha.audio.muted = false
  document.onmousemove = null
  console.log('删除事件')
}

export default function PlayControl() {

  const [paused, setPaused] = useState(ha.audio.paused)

  const playClick = () => {
    setPaused(false)
    ha.play()
  }

  const pauseClick = () => {
    setPaused(true)
    ha.pause()
  }

  const previousClick = () => {
    ha.previous()
  }

  const nextClick = () => {
    ha.next()
  }

  return (
    <Row justify="space-around" align="middle">
      <Col flex="180px">
        <StepBackwardOutlined onClick={previousClick} style={{ fontSize: '30px', color: '#03a9f4' }} />
        {
          paused ?
            <PlayCircleOutlined onClick={playClick} style={{ fontSize: '35px', color: '#03a9f4', margin: '0 15px' }} />
            :
            <PauseCircleOutlined onClick={pauseClick} style={{ fontSize: '35px', color: '#03a9f4', margin: '0 15px' }} />
        }
        <StepForwardOutlined onClick={nextClick} style={{ fontSize: '30px', color: '#03a9f4' }} />
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