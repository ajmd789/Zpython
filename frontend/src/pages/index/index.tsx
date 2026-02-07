import { View, Text, Button, ScrollView, Navigator } from '@tarojs/components'
import { useLoad, navigateTo, redirectTo } from '@tarojs/taro'
import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import './index.scss'

const BASE_URL = 'https://haoguozhi.com'

interface IpRecord {
  id: number
  ip_address: string
  visit_time: string
}

export default function Index () {
  const { isAuthenticated, user, logout } = useAuth()
  const [records, setRecords] = useState<IpRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [totalCount, setTotalCount] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)

  useLoad(() => {
    console.log('Page loaded.')
  })

  const handleLogout = async () => {
    await logout()
    // 登出后刷新页面
    window.location.reload()
  }

  const fetchIpRecords = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${BASE_URL}/apipy/api/get_ip_records/?page=${page}&page_size=${pageSize}`)
      const data = await response.json()

      if (data.code === 200) {
        setRecords(data.data.records)
        setTotalCount(data.data.total_count)
      } else {
        setError(data.message || '获取 IP 记录失败')
      }
    } catch (err) {
      setError('网络请求失败，请检查网络连接')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchIpRecords()
  }, [page])

  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1)
    }
  }

  const handleNextPage = () => {
    const totalPages = Math.ceil(totalCount / pageSize)
    if (page < totalPages) {
      setPage(page + 1)
    }
  }

  return (
    <View className='index'>
      {/* 顶部导航栏 */}
      <View className='navbar'>
        <Text className='navbar-title'>IP 访问记录</Text>
        <View className='auth-buttons'>
          {isAuthenticated ? (
            <>
              <Text className='user-info'>欢迎，{user?.nickname || user?.username}</Text>
              <Button onClick={handleLogout} className='logout-button'>
                登出
              </Button>
            </>
          ) : (
            <>
              <Navigator url='/pages/login/index' className='nav-button'>
                <Button className='login-button'>登录</Button>
              </Navigator>
              <Navigator url='/pages/register/index' className='nav-button'>
                <Button className='register-button'>注册</Button>
              </Navigator>
            </>
          )}
        </View>
      </View>

      <View className='content'>
        {error && <Text className='error'>{error}</Text>}

        {loading ? (
          <Text className='loading'>加载中...</Text>
        ) : (
          <>
            <ScrollView style={{ height: '400px' }} scrollY>
              {records.length > 0 ? (
                records.map((record) => (
                  <View key={record.id} className='record-item'>
                    <Text className='record-id'>ID: {record.id}</Text>
                    <Text className='record-ip'>IP: {record.ip_address}</Text>
                    <Text className='record-time'>时间: {record.visit_time}</Text>
                  </View>
                ))
              ) : (
                <Text className='no-data'>暂无数据</Text>
              )}
            </ScrollView>

            <View className='pagination'>
              <Button
                onClick={handlePrevPage}
                disabled={page === 1}
                className='page-button'
              >
                上一页
              </Button>
              <Text className='page-info'>
                第 {page} 页，共 {Math.ceil(totalCount / pageSize)} 页
              </Text>
              <Button
                onClick={handleNextPage}
                disabled={page >= Math.ceil(totalCount / pageSize)}
                className='page-button'
              >
                下一页
              </Button>
            </View>

            <Button onClick={fetchIpRecords} className='refresh-button'>
              刷新数据
            </Button>
          </>
        )}
      </View>
    </View>
  )
}
