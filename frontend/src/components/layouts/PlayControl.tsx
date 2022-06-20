import React, { useState, useEffect } from 'react';
import { Col, Row, Slider, Dropdown, Space, Menu, Avatar, Comment, Tooltip, message } from 'antd'
import { PlayCircleOutlined, StepBackwardOutlined, StepForwardOutlined, PauseCircleOutlined, DownOutlined } from '@ant-design/icons';
import styles from './PlayControl.less';
import { ha } from '../../http/cloudMusic'
import { formatTime } from '../../utils/format'

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

  const [paused, setPaused] = useState(ha.audio.paused)
  const [position, setPosition] = useState(0)
  const [volume, setVolume] = useState(1)
  const [song, setSong] = useState('云音乐')
  const [singer, setSinger] = useState('小可爱')
  const [pic, setPic] = useState('https://www.home-assistant.io/images/favicon-192x192.png')

  const playClick = () => {
    setPaused(false)
    ha.play()
    message.success('播放音乐')
  }

  const pauseClick = () => {
    setPaused(true)
    ha.pause()
    message.success('暂停音乐')
  }

  const previousClick = () => {
    ha.previous()
    message.success('上一曲')
  }

  const nextClick = () => {
    ha.next()
    message.success('下一曲')
  }

  useEffect(() => {
    const { audio } = ha
    const ontimeupdate = () => {
      setPosition(audio.currentTime / audio.duration * 100)
      setVolume(audio.volume)
      setSinger(ha.attrs.artist)
      setPic(ha.attrs.image)
      setSong(ha.attrs.title)
    }
    audio.addEventListener('timeupdate', ontimeupdate)
    return () => {
      audio.removeEventListener('timeupdate', ontimeupdate)
    }
  }, [])

  const formatPosition: any = (value: number) => `${formatTime(ha.audio.currentTime)}/${formatTime(ha.audio.duration)}`;
  const formatVolume: any = (value: number) => `${value * 100}%`;

  return (
    <Row justify="space-around" align="middle">
      <Col flex="170px">
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
        <Comment
          className={styles.comment}
          author={<a>{song}</a>}
          avatar={<Avatar src={pic} alt={song} />}
          content={
            <Slider defaultValue={100} value={position} step={0.1} tipFormatter={formatPosition} />
          }
          datetime={
            <span>{singer}</span>
          }
        />
      </Col>
      <Col flex="150px">
        <Slider defaultValue={1} value={volume} min={0} max={1} step={0.1} tipFormatter={formatVolume} />
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