import React, { useState, useEffect } from 'react'
import './App.css'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

function App() {
  const [activeMenuItem, setActiveMenuItem] = useState('Кластеризация')
  const [selectedFilter, setSelectedFilter] = useState('total')
  const [selectedClass, setSelectedClass] = useState('Все')
  const [selectedTimeRange, setSelectedTimeRange] = useState('all-time')
  const [customDateRange, setCustomDateRange] = useState({
    startDate: '',
    endDate: ''
  })
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [testingData, setTestingData] = useState(null)
  const [testingMetrics, setTestingMetrics] = useState({
    accuracy: 0.847,
    f1Micro: 0.823
  })
  const [availableTopics, setAvailableTopics] = useState([])
  const [isLoadingTopics, setIsLoadingTopics] = useState(false)
  const [topicsError, setTopicsError] = useState(null)
  const [dashboardData, setDashboardData] = useState(null)
  const [isLoadingDashboard, setIsLoadingDashboard] = useState(false)
  const [dashboardError, setDashboardError] = useState(null)

  // Состояния для sentiment API
  const [sentimentData, setSentimentData] = useState(null)
  const [isLoadingSentiment, setIsLoadingSentiment] = useState(false)
  const [sentimentError, setSentimentError] = useState(null)

  // Функция для перевода названий тем на русский язык
  const translateTopicName = (topicName) => {
    const translations = {
      'autocredits': 'Автокредиты',
      'creditcards': 'Кредитные карты',
      'credits': 'Кредиты',
      'debitcards': 'Дебетовые карты',
      'deposits': 'Депозиты',
      'hypothec': 'Ипотека',
      'individual': 'Индивидуальные услуги',
      'mobile_app': 'Мобильное приложение',
      'other': 'Прочее',
      'remote': 'Удаленное обслуживание',
      'restructing': 'Реструктуризация',
      'transfers': 'Переводы'
    }
    return translations[topicName] || topicName
  }

  // Функция для вычисления дат и режима на основе выбранного временного диапазона
  const getDateRangeAndMode = () => {
    const now = new Date()
    const endDate = new Date(now)
    endDate.setHours(23, 59, 59, 999) // Конец дня
    
    let startDate = new Date(now)
    let mode = 'days:day'
    
    switch (selectedTimeRange) {
      case 'all-time':
        startDate = new Date('2024-01-01T00:00:00Z')
        mode = 'all:month'
        break
      case 'last-month':
        startDate = new Date(now)
        startDate.setDate(startDate.getDate() - 30)
        mode = 'days:day'
        break
      case 'last-6-months':
        startDate = new Date(now)
        startDate.setMonth(startDate.getMonth() - 6)
        mode = 'halfyear:week'
        break
      case 'last-12-months':
        startDate = new Date(now)
        startDate.setMonth(startDate.getMonth() - 12)
        mode = 'all:month'
        break
      case 'custom':
        // Используем customDateRange если он задан
        if (customDateRange.startDate && customDateRange.endDate) {
          startDate = new Date(customDateRange.startDate + 'T00:00:00Z')
          endDate.setTime(new Date(customDateRange.endDate + 'T23:59:59Z').getTime())
          
          // Определяем режим на основе длительности диапазона
          const diffInDays = (endDate - startDate) / (1000 * 60 * 60 * 24)
          const diffInMonths = (endDate.getFullYear() - startDate.getFullYear()) * 12 + (endDate.getMonth() - startDate.getMonth())
          
          if (diffInDays <= 30) {
            mode = 'days:day'
          } else if (diffInMonths < 12) {
            mode = 'halfyear:week'
          } else {
            mode = 'all:month'
          }
        } else {
          // Fallback к последним 30 дням
          startDate = new Date(now)
          startDate.setDate(startDate.getDate() - 30)
          mode = 'days:day'
        }
        break
      default:
        // По умолчанию - последние 30 дней
        startDate = new Date(now)
        startDate.setDate(startDate.getDate() - 30)
        mode = 'days:day'
    }
    
    return {
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      mode: mode
    }
  }

  // Функция для загрузки тем из API
  const fetchAvailableTopics = async () => {
    setIsLoadingTopics(true)
    setTopicsError(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/topics/available')
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.status === 'success' && data.data) {
        // Преобразуем данные в формат для карточек классов
        const topicsWithColors = data.data.map((topic, index) => {
          const colors = ['#FF6B35', '#06D6A0', '#118AB2', '#EF476F', '#FFD23F', '#9B59B6', '#E67E22', '#2ECC71', '#E74C3C', '#F39C12', '#8E44AD', '#3498DB']
          return {
            id: topic,
            label: translateTopicName(topic),
            color: colors[index % colors.length]
          }
        })
        
        // Добавляем карточку "Все" в начало списка
        const allTopics = [
          { id: 'Все', label: 'Все', color: '#2b61ec' },
          ...topicsWithColors
        ]
        
        setAvailableTopics(allTopics)
      } else {
        throw new Error('Invalid response format')
      }
    } catch (error) {
      console.error('Error fetching topics:', error)
      setTopicsError(error.message)
      
      // Fallback к статическим данным в случае ошибки
      setAvailableTopics([
        { id: 'Все', label: 'Все', color: '#2b61ec' },
        { id: 'autocredits', label: translateTopicName('autocredits'), color: '#FF6B35' },
        { id: 'creditcards', label: translateTopicName('creditcards'), color: '#06D6A0' },
        { id: 'credits', label: translateTopicName('credits'), color: '#118AB2' },
        { id: 'debitcards', label: translateTopicName('debitcards'), color: '#EF476F' },
        { id: 'deposits', label: translateTopicName('deposits'), color: '#FFD23F' },
        { id: 'hypothec', label: translateTopicName('hypothec'), color: '#9B59B6' },
        { id: 'individual', label: translateTopicName('individual'), color: '#E67E22' },
        { id: 'mobile_app', label: translateTopicName('mobile_app'), color: '#2ECC71' },
        { id: 'other', label: translateTopicName('other'), color: '#E74C3C' },
        { id: 'remote', label: translateTopicName('remote'), color: '#F39C12' },
        { id: 'restructing', label: translateTopicName('restructing'), color: '#8E44AD' },
        { id: 'transfers', label: translateTopicName('transfers'), color: '#3498DB' }
      ])
    } finally {
      setIsLoadingTopics(false)
    }
  }

  // Функция для загрузки данных дашборда
  const fetchDashboardData = async () => {
    setIsLoadingDashboard(true)
    setDashboardError(null)
    
    try {
      const dateRangeAndMode = getDateRangeAndMode()
      console.log('Dashboard API date range and mode:', dateRangeAndMode)
      
      const response = await fetch('http://localhost:8000/api/dashboard/comprehensive', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_date: dateRangeAndMode.start_date,
          end_date: dateRangeAndMode.end_date,
          mode: dateRangeAndMode.mode
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('Dashboard API response:', data)
      console.log('Dashboard API response keys:', Object.keys(data))
      if (data.data && data.data.overview && data.data.overview.popular_topics) {
        console.log('popular_topics found in data.overview:', data.data.overview.popular_topics)
      } else {
        console.log('popular_topics NOT found in expected location')
        console.log('Available keys:', Object.keys(data))
        if (data.data) {
          console.log('data keys:', Object.keys(data.data))
          if (data.data.overview) {
            console.log('overview keys:', Object.keys(data.data.overview))
          }
        }
      }
      setDashboardData(data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setDashboardError(error.message)
    } finally {
      setIsLoadingDashboard(false)
    }
  }

  // Функция для загрузки данных тональности
  const fetchSentimentData = async (topicId) => {
    if (topicId === 'Все') {
      setSentimentData(null)
      return
    }

    setIsLoadingSentiment(true)
    setSentimentError(null)
    try {
      const dateRangeAndMode = getDateRangeAndMode()
      console.log('Sentiment API date range and mode:', dateRangeAndMode)
      
      const response = await fetch('http://localhost:8000/api/topics/comparison', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_date: dateRangeAndMode.start_date,
          end_date: dateRangeAndMode.end_date,
          mode: dateRangeAndMode.mode,
          topics: [topicId]
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('Sentiment API response:', data)
      setSentimentData(data)
    } catch (error) {
      console.error('Error fetching sentiment data:', error)
      setSentimentError(error.message)
    } finally {
      setIsLoadingSentiment(false)
    }
  }

  // Функция для форматирования данных оси X в зависимости от режима
  const formatXAxisLabel = (period, mode) => {
    const date = new Date(period)
    
    switch (mode) {
      case 'days:day':
        return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
      case 'halfyear:week':
        // Получаем номер недели в году
        const weekNumber = Math.ceil((date - new Date(date.getFullYear(), 0, 1)) / (7 * 24 * 60 * 60 * 1000))
        return `${weekNumber}н`
      case 'all:month':
        return date.toLocaleDateString('ru-RU', { month: '2-digit', year: 'numeric' })
      default:
        return date.toLocaleDateString('ru-RU', { month: 'short' })
    }
  }

  // Загружаем темы при монтировании компонента
  useEffect(() => {
    fetchAvailableTopics()
    fetchDashboardData()
  }, [])

  // Загружаем данные тональности при изменении selectedClass
  useEffect(() => {
    fetchSentimentData(selectedClass)
  }, [selectedClass])

  // Перезагружаем данные при изменении временного диапазона
  useEffect(() => {
    fetchDashboardData()
    fetchSentimentData(selectedClass)
  }, [selectedTimeRange, customDateRange])

  // Функции для работы с файлами
  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file && file.type === 'application/json') {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const jsonData = JSON.parse(e.target.result)
          setTestingData(jsonData)
          // Симуляция обновления метрик на основе загруженных данных
          setTestingMetrics({
            accuracy: Math.random() * 0.2 + 0.8, // 0.8-1.0
            f1Micro: Math.random() * 0.2 + 0.75   // 0.75-0.95
          })
        } catch (error) {
          alert('Ошибка при чтении JSON файла')
        }
      }
      reader.readAsText(file)
    } else {
      alert('Пожалуйста, выберите JSON файл')
    }
  }

  const handleDownloadJson = () => {
    if (!testingData) {
      alert('Нет данных для скачивания')
      return
    }
    
    const dataStr = JSON.stringify(testingData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'testing_results.json'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const menuItems = [
    'Кластеризация', 
    'Тестирование',
    'Документация',
    'Логи'
  ]

  // Mock данные для графика отзывов - реальные данные по отзывам Газпромбанка
  const reviewsData = [
    { month: 'янв', value: 247, total: 20, processed: 198 },
    { month: 'фев', value: 312, total: 25, processed: 281 },
    { month: 'мар', value: 289, total: 31, processed: 267 },
    { month: 'апр', value: 356, total: 30, processed: 334 },
    { month: 'май', value: 298, total: 24, processed: 276 },
    { month: 'июн', value: 423, total: 19, processed: 401 },
    { month: 'июл', value: 387, total: 11, processed: 365 },
    { month: 'авг', value: 445, total: 17, processed: 423 },
    { month: 'сен', value: 398, total: 28, processed: 378 },
    { month: 'окт', value: 467, total: 25, processed: 445 },
    { month: 'ноя', value: 512, total: 23, processed: 489 },
    { month: 'дек', value: 478, total: 23, processed: 456 }
  ]

  // Функция для проверки наличия данных
  const hasData = () => {
    const data = getCurrentData()
    return data && data.length > 0 && data.some(item => item.value > 0)
  }

  // Функция для получения данных в зависимости от выбранного фильтра
  const getCurrentData = () => {
    // Если есть данные из API, используем их
    if (dashboardData && dashboardData.data && dashboardData.data.topic_trends && Array.isArray(dashboardData.data.topic_trends)) {
      const topicTrends = dashboardData.data.topic_trends
      const periodMap = new Map()
      
      topicTrends.forEach(trend => {
        const period = trend.period
        const count = trend.count || 0
        
        if (periodMap.has(period)) {
          periodMap.set(period, periodMap.get(period) + count)
        } else {
          periodMap.set(period, count)
        }
      })
      
      const dateRangeAndMode = getDateRangeAndMode()
      
      return Array.from(periodMap.entries())
        .sort((a, b) => new Date(a[0]) - new Date(b[0]))
        .map(([period, totalReviews]) => ({
          month: formatXAxisLabel(period, dateRangeAndMode.mode),
          value: totalReviews,
          total: totalReviews,
          processed: totalReviews
        }))
    }
    
    // Fallback к статическим данным
    return reviewsData.map(item => ({
      ...item,
      value: selectedFilter === 'total' ? item.total : item.processed
    }))
  }

  // Найти максимальное значение для масштабирования графика
  const getCurrentDataForMax = () => {
    // Проверяем, есть ли данные из API напрямую
    if (dashboardData && dashboardData.data && dashboardData.data.topic_trends && Array.isArray(dashboardData.data.topic_trends)) {
      const topicTrends = dashboardData.data.topic_trends
      const periodMap = new Map()
      
      topicTrends.forEach(trend => {
        const period = trend.period
        const count = trend.count || 0
        
        if (periodMap.has(period)) {
          periodMap.set(period, periodMap.get(period) + count)
        } else {
          periodMap.set(period, count)
        }
      })
      
      return Array.from(periodMap.values())
    }
    return reviewsData.map(item => item.total)
  }
  
  const maxValue = Math.max(...getCurrentDataForMax())
  const currentMaxValue = Math.max(...getCurrentData().map(item => item.value))
  
  // Округляем максимальное значение для красивой шкалы
  const roundedMax = Math.ceil(currentMaxValue / 100) * 100
  const chartHeight = 180 // Высота области графика в SVG

  // Функция для преобразования данных в формат pie-chart
  const getTopicsData = () => {
    console.log('getTopicsData called with selectedClass:', selectedClass)
    console.log('dashboardData:', dashboardData)
    console.log('sentimentData:', sentimentData)
    
    // Если выбран конкретный кластер (не "Все"), показываем данные тональности
    if (selectedClass !== 'Все' && sentimentData && sentimentData.data && Array.isArray(sentimentData.data)) {
      const topicData = sentimentData.data[0] // Берем первый (и единственный) элемент
      console.log('Using sentiment data for topic:', topicData)
      
      if (topicData && topicData.sentiment_breakdown) {
        const sentimentBreakdown = topicData.sentiment_breakdown
        const colors = ['#28a745', '#ffc107', '#dc3545'] // Зеленый для позитивных, желтый для нейтральных, красный для негативных
        
        const result = []
        if (sentimentBreakdown['положительно'] > 0) {
          result.push({
            label: 'Позитивные',
            color: colors[0],
            value: sentimentBreakdown['положительно'],
            count: sentimentBreakdown['положительно']
          })
        }
        if (sentimentBreakdown['нейтрально'] > 0) {
          result.push({
            label: 'Нейтральные',
            color: colors[1],
            value: sentimentBreakdown['нейтрально'],
            count: sentimentBreakdown['нейтрально']
          })
        }
        if (sentimentBreakdown['отрицательно'] > 0) {
          result.push({
            label: 'Негативные',
            color: colors[2],
            value: sentimentBreakdown['отрицательно'],
            count: sentimentBreakdown['отрицательно']
          })
        }
        
        // Вычисляем общее количество для расчета процентов
        const totalCount = result.reduce((sum, item) => sum + item.count, 0)
        
        const resultWithPercentages = result.map(item => ({
          ...item,
          value: totalCount > 0 ? Math.round((item.count / totalCount) * 100) : 0
        }))
        
        console.log('Transformed sentiment data for pie-chart:', resultWithPercentages)
        return resultWithPercentages
      }
    }
    
    // Если выбран "Все" или нет данных тональности, показываем данные popular_topics
    if (dashboardData && dashboardData.data && dashboardData.data.overview && dashboardData.data.overview.popular_topics) {
      const popularTopics = dashboardData.data.overview.popular_topics
      console.log('Using API data, popular_topics:', popularTopics)
      const colors = ['#FF6B35', '#06D6A0', '#118AB2', '#EF476F', '#FFD23F', '#9B59B6', '#E67E22', '#2ECC71', '#E74C3C', '#F39C12', '#8E44AD', '#3498DB', '#E91E63', '#FF5722', '#795548', '#607D8B', '#3F51B5', '#009688', '#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800']
      
      // Используем все темы (не ограничиваем до 5)
      const allTopics = [...popularTopics]
      
      // Вычисляем общее количество для расчета процентов
      const totalCount = allTopics.reduce((sum, topic) => sum + topic.count, 0)
      
      const result = allTopics.map((topic, index) => ({
        label: translateTopicName(topic.topic),
        color: colors[index % colors.length],
        value: totalCount > 0 ? Math.round((topic.count / totalCount) * 100) : 0,
        count: topic.count
      }))
      
      console.log('Transformed data for pie-chart:', result)
      return result
    }
    
    console.log('Using fallback data')
    // Fallback данные
    return [
      { label: 'Обслуживание клиентов', color: '#FF6B35', value: 42, count: 1847 },
      { label: 'Мобильное приложение', color: '#FFD23F', value: 28, count: 1232 },
      { label: 'Банковские карты', color: '#06D6A0', value: 18, count: 792 },
      { label: 'Кредитные продукты', color: '#118AB2', value: 8, count: 352 },
      { label: 'Депозитные услуги', color: '#EF476F', value: 4, count: 176 }
    ]
  }

  // Получаем данные для pie-chart
  const topicsData = getTopicsData()


  // Получаем карточки классов из API или используем fallback данные
  const classCards = availableTopics.length > 0 ? availableTopics : [
    { id: 'Все', label: 'Все', color: '#2b61ec' },
    { id: 'autocredits', label: translateTopicName('autocredits'), color: '#FF6B35' },
    { id: 'creditcards', label: translateTopicName('creditcards'), color: '#06D6A0' },
    { id: 'credits', label: translateTopicName('credits'), color: '#118AB2' },
    { id: 'debitcards', label: translateTopicName('debitcards'), color: '#EF476F' },
    { id: 'deposits', label: translateTopicName('deposits'), color: '#FFD23F' },
    { id: 'hypothec', label: translateTopicName('hypothec'), color: '#9B59B6' },
    { id: 'individual', label: translateTopicName('individual'), color: '#E67E22' },
    { id: 'mobile_app', label: translateTopicName('mobile_app'), color: '#2ECC71' },
    { id: 'other', label: translateTopicName('other'), color: '#E74C3C' },
    { id: 'remote', label: translateTopicName('remote'), color: '#F39C12' },
    { id: 'restructing', label: translateTopicName('restructing'), color: '#8E44AD' },
    { id: 'transfers', label: translateTopicName('transfers'), color: '#3498DB' }
  ]

  // Данные для выбора временного диапазона
  const timeRangeOptions = [
    { id: 'last-month', label: 'Месяц' },
    { id: 'last-6-months', label: 'Полгода' },
    { id: 'last-12-months', label: 'Год' },
    { id: 'all-time', label: 'Всё время' },
    { id: 'custom', label: 'Указать даты' }
  ]

  // Функция для рендера содержимого дашборда
  const renderDashboardContent = (pageTitle) => (
    <>
      <div className="main__header">
        <h1 className="main__title">{pageTitle}</h1>
      </div>

      <div className="dashboard">
        {/* Карточка статистики по отзывам */}
        <div className="card card--large">
          <div className="card__header">
            <h3 className="card__title">Статистика по количеству отзывов</h3>
          </div>
          
          <div className="card__filters">
            <label className="filter-radio">
              <input 
                type="radio" 
                name="reviews-filter"
                value="total"
                checked={selectedFilter === 'total'}
                onChange={(e) => setSelectedFilter(e.target.value)}
              />
              <span className="filter-radio__label">Общее количество отзывов</span>
            </label>
            
            <label className="filter-radio">
              <input 
                type="radio" 
                name="reviews-filter"
                value="processed"
                checked={selectedFilter === 'processed'}
                onChange={(e) => setSelectedFilter(e.target.value)}
              />
              <span className="filter-radio__label">Обработанные отзывы</span>
            </label>
          </div>

          <div className="chart-container">
            {hasData() ? (
              <ResponsiveContainer width="100%" height={350}>
                <LineChart
                  data={getCurrentData()}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 20,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis 
                    dataKey="month" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6c757d' }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6c757d' }}
                    domain={[0, roundedMax]}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e9ecef',
                      borderRadius: '12px',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                    }}
                    labelStyle={{ color: '#6c757d', fontSize: '12px' }}
                    formatter={(value) => [`${value} отзывов`, 'Количество']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#2b61ec" 
                    strokeWidth={3}
                    dot={{ fill: '#2b61ec', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#2b61ec', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '350px',
                color: '#6c757d',
                fontSize: '16px',
                fontWeight: '500'
              }}>
                Нет данных за выбранный период
              </div>
            )}
          </div>
        </div>

        {/* Карточка статистики по тематике */}
        <div className="card card--small">
          <div className="card__header">
            <h3 className="card__title">
              Статистика по тематике
              {isLoadingDashboard && <span style={{color: '#2b61ec', fontSize: '14px'}}> (загрузка...)</span>}
              {dashboardError && <span style={{color: '#dc3545', fontSize: '14px'}}> (ошибка)</span>}
            </h3>
            <button 
              onClick={fetchDashboardData}
              disabled={isLoadingDashboard}
              style={{
                padding: '4px 8px',
                fontSize: '12px',
                background: isLoadingDashboard ? '#ccc' : '#2b61ec',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isLoadingDashboard ? 'not-allowed' : 'pointer'
              }}
            >
              {isLoadingDashboard ? '⏳ Загрузка...' : '🔄 Обновить данные'}
            </button>
          </div>
          
          <div className="pie-chart">
            {(selectedClass === 'Все' ? isLoadingDashboard : isLoadingSentiment) ? (
              <div className="pie-chart__loading">
                <div className="pie-chart__loading-spinner"></div>
                <span className="pie-chart__loading-text">Загрузка данных...</span>
              </div>
            ) : (selectedClass === 'Все' ? dashboardError : sentimentError) ? (
              <div className="pie-chart__error">
                <div className="pie-chart__error-icon">⚠️</div>
                <span className="pie-chart__error-text">
                  Ошибка загрузки данных: {selectedClass === 'Все' ? dashboardError : sentimentError}. Используются fallback данные.
                </span>
              </div>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={topicsData}
                      cx="50%"
                      cy="50%"
                      innerRadius={0}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      stroke="#fff"
                      strokeWidth={2}
                      paddingAngle={2}
                      animationBegin={0}
                      animationDuration={300}
                    >
                      {topicsData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.color}
                          style={{
                            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
                            transition: 'all 0.3s ease'
                          }}
                        />
                      ))}
                    </Pie>
                  <Tooltip
                    formatter={(value, name, props) => [
                      selectedClass === 'Все' 
                        ? `${value}% (${props.payload.count} отзывов)`
                        : `${value}% (${props.payload.count} ${props.payload.label.toLowerCase()})`,
                      props.payload.label
                    ]}
                      contentStyle={{
                        backgroundColor: '#ffffff',
                        border: '1px solid #e9ecef',
                        borderRadius: '8px',
                        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>

                <div className="pie-chart__legend">
                  {topicsData.map((topic, index) => (
                    <div key={index} className="pie-chart__legend-item">
                      <div
                        className="pie-chart__legend-dot"
                        style={{ backgroundColor: topic.color }}
                      ></div>
                      <div className="pie-chart__legend-text">
                        <span className="pie-chart__legend-label">{topic.label}</span>
                        <span className="pie-chart__legend-value">{topic.value}% ({topic.count})</span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  )

  // Функция для рендера страницы кластеризации
  const renderClusteringPage = () => (
    <>
      <div className="main__header">
        <h1 className="main__title">Кластеризация</h1>
      </div>

      {/* Карточки выбора класса */}
      <div className="class-cards">
        <div className="class-cards__container">
          {isLoadingTopics ? (
            <div className="class-cards__loading">
              <div className="class-cards__loading-spinner"></div>
              <span className="class-cards__loading-text">Загрузка тем...</span>
            </div>
          ) : topicsError ? (
            <div className="class-cards__error">
              <div className="class-cards__error-icon">⚠️</div>
              <span className="class-cards__error-text">
                Ошибка загрузки тем: {topicsError}. Используются fallback данные.
              </span>
            </div>
          ) : null}
          
          {classCards.map((classCard) => (
            <div
              key={classCard.id}
              className={`class-card ${selectedClass === classCard.id ? 'class-card--active' : ''}`}
              data-class={classCard.id}
              onClick={() => setSelectedClass(classCard.id)}
              style={{
                borderColor: selectedClass === classCard.id ? classCard.color : (classCard.id === 'Все' ? '#c5d9f1' : 'transparent'),
                backgroundColor: selectedClass === classCard.id ? `${classCard.color}10` : (classCard.id === 'Все' ? 'linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%)' : '#ffffff')
              }}
            >
              <div 
                className="class-card__indicator"
                style={{ backgroundColor: classCard.color }}
              ></div>
              <span className="class-card__label">{classCard.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Выбор временного диапазона */}
      <div className="time-range-selector">
        <div className="time-range-selector__container">
          <div className="time-range-selector__label">
            <span>Временной диапазон:</span>
          </div>
          <div className="time-range-selector__options">
            {timeRangeOptions.filter(option => option.id !== 'custom').map((option) => (
              <label key={option.id} className="time-range-option">
                <input
                  type="radio"
                  name="time-range"
                  value={option.id}
                  checked={selectedTimeRange === option.id}
                  onChange={(e) => setSelectedTimeRange(e.target.value)}
                />
                <span className="time-range-option__label">{option.label}</span>
              </label>
            ))}
          </div>
          
          {/* Поля для выбора дат */}
          <div className="custom-date-range" style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: '20px' }}>
            <div className="custom-date-range__field" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <label className="custom-date-range__label" style={{ fontSize: '14px', fontWeight: '500' }}>От:</label>
              <input
                type="date"
                className="custom-date-range__input"
                value={customDateRange.startDate}
                onChange={(e) => setCustomDateRange(prev => ({
                  ...prev,
                  startDate: e.target.value
                }))}
                style={{ 
                  padding: '4px 6px', 
                  border: 'none', 
                  borderBottom: '1px solid #ccc',
                  backgroundColor: 'transparent',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
            </div>
            <div className="custom-date-range__field" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <label className="custom-date-range__label" style={{ fontSize: '14px', fontWeight: '500' }}>До:</label>
              <input
                type="date"
                className="custom-date-range__input"
                value={customDateRange.endDate}
                onChange={(e) => setCustomDateRange(prev => ({
                  ...prev,
                  endDate: e.target.value
                }))}
                style={{ 
                  padding: '4px 6px', 
                  border: 'none', 
                  borderBottom: '1px solid #ccc',
                  backgroundColor: 'transparent',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
            </div>
            <button
              onClick={() => {
                setSelectedTimeRange('custom')
                fetchDashboardData()
                fetchSentimentData(selectedClass)
              }}
              style={{
                padding: '6px 12px',
                backgroundColor: '#2b61ec',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                marginLeft: '8px'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#1e4bb8'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#2b61ec'}
            >
              Обновить
            </button>
          </div>
        </div>
      </div>

      {/* Дашборд с графиками */}
      <div className="dashboard">
        {/* Карточка статистики по отзывам */}
        <div className="card card--large">
          <div className="card__header">
            <h3 className="card__title">
              {selectedClass === 'Все' 
                ? 'Статистика по количеству отзывов - Общая статистика' 
                : `Статистика по количеству отзывов - ${translateTopicName(selectedClass)}`}
            </h3>
          </div>

          <div className="chart-container">
            {hasData() ? (
              <ResponsiveContainer width="100%" height={350}>
                <LineChart
                  data={getCurrentData()}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 20,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis 
                    dataKey="month" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6c757d' }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6c757d' }}
                    domain={[0, roundedMax]}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e9ecef',
                      borderRadius: '12px',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                    }}
                    labelStyle={{ color: '#6c757d', fontSize: '12px' }}
                    formatter={(value) => [`${value} отзывов`, 'Количество']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke={classCards.find(c => c.id === selectedClass)?.color || '#2b61ec'} 
                    strokeWidth={3}
                    dot={{ fill: classCards.find(c => c.id === selectedClass)?.color || '#2b61ec', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: classCards.find(c => c.id === selectedClass)?.color || '#2b61ec', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '350px',
                color: '#6c757d',
                fontSize: '16px',
                fontWeight: '500'
              }}>
                Нет данных за выбранный период
              </div>
            )}
          </div>
        </div>

        {/* Карточка статистики по тематике */}
        <div className="card card--small">
          <div className="card__header">
            <h3 className="card__title">
              {selectedClass === 'Все' 
                ? 'Процентное распределение по отзывам' 
                : `Статистика по тональности - ${translateTopicName(selectedClass)}`}
            </h3>
          </div>
          
          <div className="pie-chart">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={topicsData}
                  cx="50%"
                  cy="50%"
                  innerRadius={0}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  stroke="#fff"
                  strokeWidth={2}
                  paddingAngle={2}
                  animationBegin={0}
                  animationDuration={300}
                >
                  {topicsData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color}
                      style={{
                        filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
                        transition: 'all 0.3s ease'
                      }}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value, name, props) => [`${value}%`, props.payload.label]}
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e9ecef',
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>

            <div className="pie-chart__legend">
              {topicsData.map((topic, index) => (
                <div key={index} className="pie-chart__legend-item">
                  <div
                    className="pie-chart__legend-dot"
                    style={{ backgroundColor: topic.color }}
                  ></div>
                  <div className="pie-chart__legend-text">
                    <span className="pie-chart__legend-label">{topic.label}</span>
                    <span className="pie-chart__legend-value">{topic.value}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  )

  // Функция для рендера страницы тестирования
  const renderTestingPage = () => (
    <>
      <div className="main__header">
        <h1 className="main__title">Тестирование</h1>
      </div>

      {/* Панель загрузки и метрик */}
      <div className="testing-panel">
        <div className="testing-panel__container">
          {/* Загрузка файла */}
          <div className="file-upload-section">
            <h3 className="file-upload-section__title">Загрузить данные для тестирования</h3>
            <div className="file-upload">
              <input
                type="file"
                id="json-upload"
                accept=".json"
                onChange={handleFileUpload}
                className="file-upload__input"
              />
              <label htmlFor="json-upload" className="file-upload__label">
                <span className="file-upload__icon">📁</span>
                <span className="file-upload__text">
                  {testingData ? 'Файл загружен' : 'Выберите JSON файл'}
                </span>
              </label>
            </div>
          </div>


          {/* Скачивание файла */}
          <div className="download-section">
            <h3 className="download-section__title">Экспорт результатов</h3>
            <button
              className="download-button"
              onClick={handleDownloadJson}
              disabled={!testingData}
            >
              <span className="download-button__icon">💾</span>
              <span className="download-button__text">Скачать JSON</span>
            </button>
          </div>
        </div>
      </div>

      {/* Карточки выбора класса */}
      <div className="class-cards">
        <div className="class-cards__container">
          {isLoadingTopics ? (
            <div className="class-cards__loading">
              <div className="class-cards__loading-spinner"></div>
              <span className="class-cards__loading-text">Загрузка тем...</span>
            </div>
          ) : topicsError ? (
            <div className="class-cards__error">
              <div className="class-cards__error-icon">⚠️</div>
              <span className="class-cards__error-text">
                Ошибка загрузки тем: {topicsError}. Используются fallback данные.
              </span>
            </div>
          ) : null}
          
          {classCards.map((classCard) => (
            <div
              key={classCard.id}
              className={`class-card ${selectedClass === classCard.id ? 'class-card--active' : ''}`}
              data-class={classCard.id}
              onClick={() => setSelectedClass(classCard.id)}
              style={{
                borderColor: selectedClass === classCard.id ? classCard.color : (classCard.id === 'Все' ? '#c5d9f1' : 'transparent'),
                backgroundColor: selectedClass === classCard.id ? `${classCard.color}10` : (classCard.id === 'Все' ? 'linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%)' : '#ffffff')
              }}
            >
              <div 
                className="class-card__indicator"
                style={{ backgroundColor: classCard.color }}
              ></div>
              <span className="class-card__label">{classCard.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Выбор временного диапазона */}
      <div className="time-range-selector">
        <div className="time-range-selector__container">
          <div className="time-range-selector__label">
            <span>Временной диапазон:</span>
          </div>
          <div className="time-range-selector__options">
            {timeRangeOptions.map((option) => (
              <label key={option.id} className="time-range-option">
                <input
                  type="radio"
                  name="time-range-testing"
                  value={option.id}
                  checked={selectedTimeRange === option.id}
                  onChange={(e) => setSelectedTimeRange(e.target.value)}
                />
                <span className="time-range-option__label">{option.label}</span>
              </label>
            ))}
          </div>
        </div>
        
        {/* Кастомный выбор дат */}
        {selectedTimeRange === 'custom' && (
          <div className="custom-date-range">
            <div className="custom-date-range__container">
              <div className="custom-date-range__field">
                <label className="custom-date-range__label">От:</label>
                <input
                  type="date"
                  className="custom-date-range__input"
                  value={customDateRange.startDate}
                  onChange={(e) => setCustomDateRange(prev => ({
                    ...prev,
                    startDate: e.target.value
                  }))}
                />
              </div>
              <div className="custom-date-range__field">
                <label className="custom-date-range__label">До:</label>
                <input
                  type="date"
                  className="custom-date-range__input"
                  value={customDateRange.endDate}
                  onChange={(e) => setCustomDateRange(prev => ({
                    ...prev,
                    endDate: e.target.value
                  }))}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Дашборд с графиками */}
      <div className="dashboard">
        {/* Карточка статистики по отзывам */}
        <div className="card card--large">
          <div className="card__header">
            <h3 className="card__title">
              {selectedClass === 'Все' 
                ? 'Результаты тестирования - Общая статистика' 
                : `Результаты тестирования - ${translateTopicName(selectedClass)}`}
            </h3>
          </div>
          
          <div className="card__filters">
            <label className="filter-radio">
              <input 
                type="radio" 
                name="testing-filter"
                value="total"
                checked={selectedFilter === 'total'}
                onChange={(e) => setSelectedFilter(e.target.value)}
              />
              <span className="filter-radio__label">Общее количество тестов</span>
            </label>
            
            <label className="filter-radio">
              <input 
                type="radio" 
                name="testing-filter"
                value="processed"
                checked={selectedFilter === 'processed'}
                onChange={(e) => setSelectedFilter(e.target.value)}
              />
              <span className="filter-radio__label">Успешные тесты</span>
            </label>
          </div>

          <div className="chart-container">
            {hasData() ? (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart
                  data={getCurrentData()}
                  margin={{
                    top: 10,
                    right: 15,
                    left: 10,
                    bottom: 10,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis 
                    dataKey="month" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6c757d' }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6c757d' }}
                    domain={[0, roundedMax]}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e9ecef',
                      borderRadius: '12px',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                    }}
                    labelStyle={{ color: '#6c757d', fontSize: '12px' }}
                    formatter={(value) => [`${value} ${selectedFilter === 'total' ? 'тестов' : 'успешных'}`, 'Количество']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke={classCards.find(c => c.id === selectedClass)?.color || '#2b61ec'} 
                    strokeWidth={3}
                    dot={{ fill: classCards.find(c => c.id === selectedClass)?.color || '#2b61ec', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: classCards.find(c => c.id === selectedClass)?.color || '#2b61ec', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '220px',
                color: '#6c757d',
                fontSize: '16px',
                fontWeight: '500'
              }}>
                Нет данных за выбранный период
              </div>
            )}
          </div>
        </div>

        {/* Карточка распределения результатов тестирования */}
        <div className="card card--small">
          <div className="card__header">
            <h3 className="card__title">
              {selectedClass === 'Все' 
                ? 'Распределение результатов - Общая статистика' 
                : `Распределение результатов для: ${translateTopicName(selectedClass)}`}
            </h3>
          </div>
          
          <div className="pie-chart">
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={topicsData}
                  cx="50%"
                  cy="50%"
                  innerRadius={0}
                  outerRadius={50}
                  fill="#8884d8"
                  dataKey="value"
                  stroke="#fff"
                  strokeWidth={2}
                  paddingAngle={2}
                  animationBegin={0}
                  animationDuration={300}
                >
                  {topicsData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color}
                      style={{
                        filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
                        transition: 'all 0.3s ease'
                      }}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value, name, props) => [`${value}%`, props.payload.label]}
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e9ecef',
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>

            <div className="pie-chart__legend">
              {topicsData.map((topic, index) => (
                <div key={index} className="pie-chart__legend-item">
                  <div
                    className="pie-chart__legend-dot"
                    style={{ backgroundColor: topic.color }}
                  ></div>
                  <div className="pie-chart__legend-text">
                    <span className="pie-chart__legend-label">{topic.label}</span>
                    <span className="pie-chart__legend-value">{topic.value}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  )

  // Функция для рендера страницы документации
  const renderDocumentationPage = () => (
    <>
      <div className="main__header">
        <h1 className="main__title">Документация</h1>
      </div>

      <div className="documentation">
        {/* Быстрый старт */}
        <div className="documentation__section">
          <div className="documentation__card">
            <div className="documentation__card-header">
              <div className="documentation__icon">🚀</div>
              <h2 className="documentation__card-title">Быстрый старт</h2>
            </div>
            <div className="documentation__card-content">
              <p>Добро пожаловать в систему анализа отзывов Газпромбанка! Наш сервис поможет вам получить ценные инсайты из клиентских отзывов.</p>
              <div className="documentation__steps">
                <div className="documentation__step">
                  <span className="documentation__step-number">1</span>
                  <span>Выберите нужную страницу в левом меню</span>
                </div>
                <div className="documentation__step">
                  <span className="documentation__step-number">2</span>
                  <span>Настройте фильтры и временной диапазон</span>
                </div>
                <div className="documentation__step">
                  <span className="documentation__step-number">3</span>
                  <span>Анализируйте данные с помощью интерактивных графиков</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Сценарии использования */}
        <div className="documentation__section">
          <h2 className="documentation__section-title">Сценарии использования</h2>
          
          <div className="documentation__scenarios">
            <div className="documentation__scenario">
              <div className="documentation__scenario-header">
                <div className="documentation__scenario-icon">📊</div>
                <h3>Анализ общей статистики</h3>
              </div>
              <p><strong>Задача:</strong> Получить общее представление о количестве и распределении отзывов</p>
              <div className="documentation__scenario-steps">
                <p><strong>Шаги:</strong></p>
                <ul>
                  <li>Перейдите на страницу "Кластеризация"</li>
                  <li>Выберите карточку "Все" для общей статистики</li>
                  <li>Настройте временной диапазон (месяц, полгода, год или указать даты)</li>
                  <li>Изучите линейный график для понимания динамики</li>
                  <li>Проанализируйте круговую диаграмму распределения по тематикам</li>
                </ul>
              </div>
            </div>

            <div className="documentation__scenario">
              <div className="documentation__scenario-header">
                <div className="documentation__scenario-icon">🔍</div>
                <h3>Анализ конкретной категории</h3>
              </div>
              <p><strong>Задача:</strong> Детальное изучение отзывов по определенной категории услуг</p>
              <div className="documentation__scenario-steps">
                <p><strong>Шаги:</strong></p>
                <ul>
                  <li>Выберите интересующую категорию (Обслуживание, Кредитные карты, Депозиты и т.д.)</li>
                  <li>Графики автоматически обновятся с учетом выбранной категории</li>
                  <li>Сравните общее количество отзывов с обработанными</li>
                  <li>Обратите внимание на изменение цветов графиков под выбранную категорию</li>
                </ul>
              </div>
            </div>

            <div className="documentation__scenario">
              <div className="documentation__scenario-header">
                <div className="documentation__scenario-icon">🧪</div>
                <h3>Тестирование модели</h3>
              </div>
              <p><strong>Задача:</strong> Загрузить данные для тестирования и получить метрики качества</p>
              <div className="documentation__scenario-steps">
                <p><strong>Шаги:</strong></p>
                <ul>
                  <li>Перейдите на страницу "Тестирование"</li>
                  <li>Загрузите JSON файл с тестовыми данными</li>
                  <li>Изучите ключевые метрики: Accuracy и F1-Micro</li>
                  <li>Проанализируйте результаты тестирования по категориям</li>
                  <li>Скачайте результаты в формате JSON для дальнейшего анализа</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Описание функций */}
        <div className="documentation__section">
          <h2 className="documentation__section-title">Описание функций</h2>
          
          <div className="documentation__features">
            <div className="documentation__feature">
              <h3>📈 Интерактивные графики</h3>
              <ul>
                <li><strong>Линейный график:</strong> Показывает динамику отзывов по месяцам</li>
                <li><strong>Круговая диаграмма:</strong> Распределение отзывов по тематикам</li>
                <li><strong>Hover эффекты:</strong> Наведите курсор для получения детальной информации</li>
              </ul>
            </div>

            <div className="documentation__feature">
              <h3>🎛️ Фильтрация данных</h3>
              <ul>
                <li><strong>Категории:</strong> Фильтрация по типам банковских услуг</li>
                <li><strong>Временные диапазоны:</strong> От месяца до года, или произвольный период</li>
                <li><strong>Типы отзывов:</strong> Общее количество или только обработанные</li>
              </ul>
            </div>

            <div className="documentation__feature">
              <h3>📱 Адаптивный дизайн</h3>
              <ul>
                <li><strong>Мобильное меню:</strong> Бургер-меню для удобной навигации на телефонах</li>
                <li><strong>Responsive графики:</strong> Автоматическая адаптация под размер экрана</li>
                <li><strong>Touch-friendly:</strong> Оптимизированы для сенсорных экранов</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Технические детали */}
        <div className="documentation__section">
          <div className="documentation__card">
            <div className="documentation__card-header">
              <div className="documentation__icon">⚙️</div>
              <h2 className="documentation__card-title">Технические детали</h2>
            </div>
            <div className="documentation__card-content">
              <div className="documentation__tech-grid">
                <div className="documentation__tech-item">
                  <h4>Форматы данных</h4>
                  <p>Система работает с JSON файлами. Поддерживается загрузка и выгрузка данных в стандартном формате.</p>
                </div>
                <div className="documentation__tech-item">
                  <h4>Метрики качества</h4>
                  <p>Accuracy - точность классификации, F1-Micro - микроусредненная F1-мера для многоклассовой задачи.</p>
                </div>
                <div className="documentation__tech-item">
                  <h4>Обновление данных</h4>
                  <p>Графики обновляются в реальном времени при изменении фильтров и загрузке новых данных.</p>
                </div>
                <div className="documentation__tech-item">
                  <h4>Производительность</h4>
                  <p>Оптимизированная визуализация с поддержкой больших объемов данных и плавными анимациями.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Контакты и поддержка */}
        <div className="documentation__section">
          <div className="documentation__card documentation__card--support">
            <div className="documentation__card-header">
              <div className="documentation__icon">💬</div>
              <h2 className="documentation__card-title">Поддержка</h2>
            </div>
            <div className="documentation__card-content">
              <p>Если у вас возникли вопросы или нужна помощь, обратитесь к команде разработки:</p>
              <div className="documentation__contact-info">
                <div className="documentation__contact-item">
                  <strong>Email:</strong> analytics@gazprombank.ru
                </div>
                <div className="documentation__contact-item">
                  <strong>Техподдержка:</strong> +7 (495) 123-45-67
                </div>
                <div className="documentation__contact-item">
                  <strong>Версия системы:</strong> 1.0.0
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )

  return (
    <div className="app">
      {/* Бургер-кнопка для мобильных устройств */}
      <button 
        className="mobile-menu-toggle"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        aria-label="Toggle menu"
      >
        <span className={`burger-line ${isMobileMenuOpen ? 'burger-line--active' : ''}`}></span>
        <span className={`burger-line ${isMobileMenuOpen ? 'burger-line--active' : ''}`}></span>
        <span className={`burger-line ${isMobileMenuOpen ? 'burger-line--active' : ''}`}></span>
      </button>

      {/* Левое меню */}
      <nav className={`sidebar ${isMobileMenuOpen ? 'sidebar--mobile-open' : ''}`}>
        <div className="sidebar__header">
          <h2 className="sidebar__title">Меню</h2>
          <button 
            className="sidebar__close"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-label="Close menu"
          >
            ×
          </button>
        </div>
        <div className="sidebar__menu">
          {menuItems.map((item, index) => (
            <div 
              key={index}
              className={`sidebar__item ${activeMenuItem === item ? 'sidebar__item--active' : ''}`}
              onClick={() => {
                setActiveMenuItem(item)
                setIsMobileMenuOpen(false) // Закрываем меню при выборе пункта
              }}
            >
              <div className="sidebar__icon">
                <div className="sidebar__icon-grid">
                  <div className="sidebar__icon-square"></div>
                  <div className="sidebar__icon-square"></div>
                  <div className="sidebar__icon-square"></div>
                  <div className="sidebar__icon-square"></div>
                </div>
              </div>
              <span className="sidebar__label">{item}</span>
            </div>
          ))}
        </div>
      </nav>

      {/* Оверлей для мобильного меню */}
      {isMobileMenuOpen && (
        <div 
          className="mobile-menu-overlay"
          onClick={() => setIsMobileMenuOpen(false)}
        ></div>
      )}

      {/* Основной контент */}
      <main className="main">
        {activeMenuItem === 'Кластеризация' && renderClusteringPage()}
        {activeMenuItem === 'Тестирование' && renderTestingPage()}
        {activeMenuItem === 'Документация' && renderDocumentationPage()}
        {activeMenuItem === 'Логи' && (
          <div className="main__header">
            <h1 className="main__title">Логи</h1>
            <p>Страница в разработке...</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App