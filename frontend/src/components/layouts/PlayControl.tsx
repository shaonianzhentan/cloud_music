import React, { useState } from 'react';
import { Col, Row, Slider, Dropdown, Space, Menu, } from 'antd'
import { PlayCircleOutlined, StepBackwardOutlined, StepForwardOutlined, PauseCircleOutlined, DownOutlined } from '@ant-design/icons';
import styles from './PlayControl.less';
import { getHass, cloudMusicServer } from '../../http/cloudMusic'
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

const audio = new Audio()
audio.autoplay = true
console.log(audio)
audio.ontimeupdate = _.debounce(() => {
  console.log(audio.currentTime)
  // 更新
  cloudMusicServer({
    action: 'update',
    media_position: audio.currentTime,
    media_duration: audio.duration,
    volume_level: audio.volume,
    is_volume_muted: audio.muted
  })
}, 1000)

audio.onended = () => {
  console.log('end')
}
const hass = getHass()
hass.connection.subscribeEvents(({ data }: any) => {
  console.log(data)
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
        if (audio.src) {
          audio.src = data.media_content_id
        }
        audio.play()
        break;
    }
  }
}, 'cloud_music_client')

export default function PlayControl() {

  const [paused, setPaused] = useState(audio.paused)

  const playClick = () => {
    cloudMusicServer({ action: 'play' })
    audio.play()
    setPaused(false)
  }

  const pauseClick = () => {
    cloudMusicServer({ action: 'pause' })
    audio.pause()
    setPaused(true)
  }

  const previousClick = () => {
    cloudMusicServer({ action: 'previous' })
  }

  const nextClick = () => {
    cloudMusicServer({ action: 'next' })
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