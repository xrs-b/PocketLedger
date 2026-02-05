<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择图标"
    width="600px"
    :close-on-click-modal="false"
    destroy-on-close
    append-to-body
  >
    <!-- 搜索框 -->
    <el-input
      v-model="searchKeyword"
      placeholder="搜索图标..."
      prefix-icon="Search"
      clearable
      class="search-input"
    />

    <!-- 分类标签页 -->
    <el-tabs v-model="activeTab" class="icon-tabs">
      <el-tab-pane label="收入图标" name="income">
        <div class="icon-grid">
          <div
            v-for="icon in filteredIncomeIcons"
            :key="icon.name"
            class="icon-item"
            :class="{ selected: selectedIcon === icon.name }"
            @click="selectIcon(icon.name)"
          >
            <el-icon :size="24">
              <component :is="icon.component" />
            </el-icon>
            <span class="icon-name">{{ icon.label }}</span>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="支出图标" name="expense">
        <div class="icon-grid">
          <div
            v-for="icon in filteredExpenseIcons"
            :key="icon.name"
            class="icon-item"
            :class="{ selected: selectedIcon === icon.name }"
            @click="selectIcon(icon.name)"
          >
            <el-icon :size="24">
              <component :is="icon.component" />
            </el-icon>
            <span class="icon-name">{{ icon.label }}</span>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="通用图标" name="common">
        <div class="icon-grid">
          <div
            v-for="icon in filteredCommonIcons"
            :key="icon.name"
            class="icon-item"
            :class="{ selected: selectedIcon === icon.name }"
            @click="selectIcon(icon.name)"
          >
            <el-icon :size="24">
              <component :is="icon.component" />
            </el-icon>
            <span class="icon-name">{{ icon.label }}</span>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 空状态 -->
    <el-empty
      v-if="filteredIcons.length === 0"
      description="未找到相关图标"
      :image-size="80"
    />

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Search,
  Money,
  Wallet,
  TrendCharts,
  Coin,
  CreditCard,
  Ticket,
  Discount,
  Present,
  Food,
  Van,
  ShoppingCart,
  Film,
  House,
  OfficeBuilding,
  Grid,
  Collection,
  Postcard,
  ChatDotRound,
  Iphone,
  Headset,
  Mug,
  Book,
  Basketball,
  Umbrella,
  Cigarette,
  Medical,
  Cherry,
  GobletSquareFull,
  Ghost,
  Aim,
  AlarmClock,
  AutoTimer,
  Baguette,
  Bat,
  Bee,
  Bowl,
  Box,
  Briefcase,
  Brush,
  Burger,
  Calendar,
  Camera,
  Card,
  CaretLeft,
  CaretRight,
  Connection,
  CopyDocument,
  Crop,
  DArrowLeft,
  DArrowRight,
  DataAnalysis,
  Delete,
  Dish,
  Document,
  Download,
  Edit,
  Folder,
  FolderOpened,
  Football,
  ForkSpoon,
  Fry,
  Goods,
  GridPosition,
  Handle,
  HeadSide,
  Help,
  HomeFilled,
  HotWater,
  IceCream,
  InfoFilled,
  Keyboard,
  Laptop,
  Lightning,
  Link,
  List,
  Loading,
  Location,
  Lock,
  MagicStick,
  Management,
  MapLocation,
  Menu,
  Message,
  Microphone,
  Monitor,
  Moon,
  More,
  Mouse,
  Music,
  Notification,
  Odometer,
  Opportunity,
  Orange,
  Paperclip,
  Peeling,
  Phone,
  PictureFilled,
  PieChart,
  Place,
  Platform,
  Plus,
  Position,
  Poster,
  PriceTag,
  Printer,
  QuestionFilled,
  Reading,
  Refresh,
  RefreshRight,
  Remove,
  School,
  SearchLeft,
  Service,
  Setting,
  Share,
  Ship,
  Shop,
  ShoppingBag,
  Smile,
  Snacks,
  Sort,
  Stamp,
  Star,
  Stopwatch,
  Study,
  Suny,
  Switch,
  TakeawayBox,
  TicketFilled,
  Timer,
  Tools,
  Top,
  Trash,
  Trophy,
  TurnOff,
  Upload,
  UploadFilled,
  User,
  UserFilled,
  Van,
  VideoCamera,
  View,
  Warning,
  Watch,
  WaterPower,
  Sunny,
  MoonNight,
  Drizzling,
  Pouring,
  Lightning,
  Snowy,
  Sunray,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  selected: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'expense'
  }
})

// Emits
const emit = defineEmits(['update:visible', 'update:selected'])

// 响应式数据
const searchKeyword = ref('')
const activeTab = ref('expense')
const selectedIcon = ref('')

// 图标数据
const incomeIcons = [
  { name: 'Money', label: '钱', component: Money },
  { name: 'TrendCharts', label: '趋势', component: TrendCharts },
  { name: 'Coin', label: '金币', component: Coin },
  { name: 'CreditCard', label: '信用卡', component: CreditCard },
  { name: 'Ticket', label: '优惠券', component: Ticket },
  { name: 'Discount', label: '折扣', component: Discount },
  { name: 'Present', label: '礼物', component: Present },
  { name: 'Wallet', label: '钱包', component: Wallet },
  { name: 'DataAnalysis', label: '分析', component: DataAnalysis },
  { name: 'Bank', label: '银行', component: OfficeBuilding },
  { name: 'GoldMedal', label: '奖金', component: Trophy },
  { name: 'GiftBox', label: '礼盒', component: Present }
]

const expenseIcons = [
  { name: 'Food', label: '餐饮', component: Food },
  { name: 'Van', label: '交通', component: Van },
  { name: 'ShoppingCart', label: '购物', component: ShoppingCart },
  { name: 'Film', label: '娱乐', component: Film },
  { name: 'House', label: '住房', component: House },
  { name: 'OfficeBuilding', label: '工作', component: OfficeBuilding },
  { name: 'Grid', label: '生活', component: Grid },
  { name: 'Collection', label: '收藏', component: Collection },
  { name: 'ChatDotRound', label: '社交', component: ChatDotRound },
  { name: 'Iphone', label: '通讯', component: Iphone },
  { name: 'Headset', label: '娱乐', component: Headset },
  { name: 'Mug', label: '咖啡', component: Mug },
  { name: 'Book', label: '学习', component: Book },
  { name: 'Basketball', label: '运动', component: Basketball },
  { name: 'Umbrella', label: '保险', component: Umbrella },
  { name: 'Cigarette', label: '烟酒', component: Cigarette },
  { name: 'Medical', label: '医疗', component: Medical },
  { name: 'Cherry', label: '水果', component: Cherry },
  { name: 'ShoppingBag', label: '购物', component: ShoppingBag },
  { name: 'Goods', label: '日用品', component: Goods }
]

const commonIcons = [
  { name: 'Folder', label: '文件夹', component: Folder },
  { name: 'FolderOpened', label: '打开文件夹', component: FolderOpened },
  { name: 'Document', label: '文档', component: Document },
  { name: 'PictureFilled', label: '图片', component: PictureFilled },
  { name: 'Star', label: '星标', component: Star },
  { name: 'Setting', label: '设置', component: Setting },
  { name: 'Delete', label: '删除', component: Delete },
  { name: 'Edit', label: '编辑', component: Edit },
  { name: 'Plus', label: '添加', component: Plus },
  { name: 'Remove', label: '移除', component: Remove },
  { name: 'Search', label: '搜索', component: Search },
  { name: 'View', label: '查看', component: View },
  { name: 'InfoFilled', label: '信息', component: InfoFilled },
  { name: 'Warning', label: '警告', component: Warning },
  { name: 'QuestionFilled', label: '帮助', component: QuestionFilled },
  { name: 'Success', label: '成功', component: CircleCheck },
  { name: 'CircleClose', label: '关闭', component: CircleClose }
]

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const filteredIncomeIcons = computed(() => {
  if (!searchKeyword.value) return incomeIcons
  const keyword = searchKeyword.value.toLowerCase()
  return incomeIcons.filter(
    icon => icon.label.toLowerCase().includes(keyword) || 
            icon.name.toLowerCase().includes(keyword)
  )
})

const filteredExpenseIcons = computed(() => {
  if (!searchKeyword.value) return expenseIcons
  const keyword = searchKeyword.value.toLowerCase()
  return expenseIcons.filter(
    icon => icon.label.toLowerCase().includes(keyword) || 
            icon.name.toLowerCase().includes(keyword)
  )
})

const filteredCommonIcons = computed(() => {
  if (!searchKeyword.value) return commonIcons
  const keyword = searchKeyword.value.toLowerCase()
  return commonIcons.filter(
    icon => icon.label.toLowerCase().includes(keyword) || 
            icon.name.toLowerCase().includes(keyword)
  )
})

const filteredIcons = computed(() => {
  switch (activeTab.value) {
    case 'income':
      return filteredIncomeIcons.value
    case 'expense':
      return filteredExpenseIcons.value
    case 'common':
      return filteredCommonIcons.value
    default:
      return []
  }
})

// 方法
const selectIcon = (iconName) => {
  selectedIcon.value = iconName
}

const handleClose = () => {
  dialogVisible.value = false
}

const handleConfirm = () => {
  emit('update:selected', selectedIcon.value)
  dialogVisible.value = false
}

// 监听 visible 变化
watch(() => props.visible, (val) => {
  if (val) {
    // 打开弹窗时设置选中状态和默认标签页
    selectedIcon.value = props.selected
    activeTab.value = props.type === 'income' ? 'income' : 'expense'
    searchKeyword.value = ''
  }
})
</script>

<style scoped>
.search-input {
  margin-bottom: 16px;
}

.icon-tabs {
  max-height: 400px;
  overflow-y: auto;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  padding: 8px 0;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  border: 2px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.icon-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.icon-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
  color: #409eff;
}

.icon-name {
  font-size: 12px;
  margin-top: 4px;
  color: #606266;
  text-align: center;
}

.icon-item.selected .icon-name {
  color: #409eff;
}

:deep(.el-tabs__header) {
  margin-bottom: 16px;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}
</style>
