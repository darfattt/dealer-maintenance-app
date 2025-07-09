# Dashboard Navigation Guide

## Overview
This document provides comprehensive guidance for implementing and extending the dashboard navigation system in the Dealer Management Application. The system follows a consistent pattern for creating sub-dashboards and detail views.

## Current Dashboard Structure

### Main Dashboard (`/dashboard`)
The main dashboard serves as the central hub with multiple widget sections:

#### Sales Column (Left)
- **Row 1**: 2 widgets (StatusSPKWidget, PaymentTypeWidget)
- **Row 2**: 3 widgets (TopDealingWidget, TopDriverWidget, DealingProcessDataHistoryWidget)

#### Inventory Column (Right)
- **Row 1**: UnitInboundStatusWidget (clickable title → Unit Inbound Detail)
- **Row 2**: PartsInboundStatusWidget

### Sub-Dashboards

#### 1. Prospecting Activity Detail (`/prospecting-activity`)
**Navigation**: Click "Prospecting Activity" title
**Layout**: 2-column layout
- **Left Column**: 2 rows (StatusSPKWidget reused + Top5ProspectWidget)
- **Right Column**: 1 widget (DataHistoryWidget with prospect data)

#### 2. Unit Inbound Detail (`/unit-inbound-detail`)
**Navigation**: Click "Data Inbound" title
**Layout**: 2-column layout
- **Left Column**: 2 rows (UnitInboundStatusWidget reused + Top5PenerimaanUnitWidget)
- **Right Column**: 1 widget (UnitInboundDataHistoryWidget)

## Navigation Implementation Pattern

### 1. Main Dashboard Setup
```vue
<!-- Dashboard.vue -->
<template>
  <!-- Clickable Title -->
  <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200 cursor-pointer hover:bg-surface-50 transition-colors duration-200" 
       @click="navigateToDetailView">
    <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">
      {{ widgetTitle }}
    </h3>
  </div>
  
  <!-- Widget Content -->
  <div class="widget-with-title">
    <WidgetComponent :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const navigateToDetailView = () => {
    router.push('/detail-view-route');
};
</script>
```

### 2. Router Configuration
```javascript
// router/index.js
{
    path: '/detail-view-route',
    name: 'detail-view-name',
    component: () => import('@/views/DetailView.vue')
}
```

### 3. Detail View Structure
```vue
<!-- DetailView.vue -->
<template>
  <div class="p-6 bg-surface-50 min-h-screen">
    <!-- Header with date filters -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-surface-900 mb-4">Detail View Title</h1>
      <!-- Date filter controls -->
    </div>

    <!-- 2-Column Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Left Column (2 rows) -->
      <div class="space-y-6">
        <!-- Row 1: Reused Widget -->
        <div>
          <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Widget Title</h3>
          </div>
          <div class="widget-with-title">
            <ReusedWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
          </div>
        </div>
        
        <!-- Row 2: New Top5 Widget -->
        <div>
          <div class="bg-surface-0 p-3 rounded-t-lg border border-b-0 border-surface-200">
            <h3 class="text-sm font-bold text-surface-900 uppercase tracking-wide">Top 5 Widget Title</h3>
          </div>
          <div class="widget-with-title">
            <Top5Widget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
          </div>
        </div>
      </div>

      <!-- Right Column (1 widget) -->
      <div class="h-full flex flex-col">
        <div class="flex-1">
          <DataHistoryWidget :dealerId="selectedDealer" :dateFrom="formattedDateFrom" :dateTo="formattedDateTo" />
        </div>
      </div>
    </div>
  </div>
</template>
```

## Widget Development Patterns

### 1. Reusable Status Widgets
- Use existing widgets without modification
- Pass props: `dealerId`, `dateFrom`, `dateTo`
- Maintain all existing functionality

### 2. Top5 Widgets (Image/Title/Total Pattern)
```vue
<!-- Top5Widget.vue -->
<template>
  <Card class="h-full">
    <template #content>
      <div class="space-y-4">
        <div v-for="item in topItems" :key="item.id" 
             class="flex items-center space-x-4 p-3 rounded-lg border border-surface-200 hover:bg-surface-50 transition-colors">
          <!-- Image -->
          <div class="flex-shrink-0">
            <img :src="item.image" :alt="item.name" 
                 class="w-12 h-12 object-cover rounded-lg border-2 border-surface-200"
                 @error="$event.target.src = 'DEFAULT_IMAGE_URL'" />
          </div>
          
          <!-- Details -->
          <div class="flex-grow min-w-0">
            <h4 class="font-bold text-base text-surface-900 truncate">{{ item.name }}</h4>
            <p class="text-sm text-surface-600">{{ item.description }}</p>
          </div>
          
          <!-- Total -->
          <div class="flex-shrink-0 text-right">
            <div class="text-2xl font-bold text-red-500">{{ item.total }}</div>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>
```

### 3. Data History Widgets (Tabular Pattern)
```vue
<!-- DataHistoryWidget.vue -->
<template>
  <Card class="h-full">
    <template #title>
      <div class="flex justify-between items-center">
        <span class="text-sm font-bold uppercase">DATA HISTORY TITLE</span>
        <div class="flex items-center space-x-2">
          <Button icon="pi pi-filter" size="small" text severity="secondary" class="p-1" />
          <Button icon="pi pi-download" size="small" text severity="secondary" class="p-1" />
        </div>
      </div>
    </template>
    
    <template #content>
      <div class="space-y-4">
        <DataTable :value="data" :loading="loading" stripedRows size="small" class="text-xs">
          <!-- Define columns based on requirements -->
        </DataTable>
        
        <!-- Pagination -->
        <div class="flex justify-between items-center pt-4 border-t border-surface-200">
          <div class="text-xs text-muted-color">
            Showing {{ first + 1 }} to {{ Math.min(first + rows, totalRecords) }} of {{ totalRecords }} entries
          </div>
          <Paginator :first="first" :rows="rows" :totalRecords="totalRecords" 
                     :rowsPerPageOptions="[10, 20, 50]" @page="onPageChange" />
        </div>
      </div>
    </template>
  </Card>
</template>
```

## Default Images Configuration

### Motorcycle/Unit Images
```javascript
// Default motorcycle image for unit widgets
const defaultMotorcycleImage = 'https://via.placeholder.com/48x48/FF5722/FFFFFF?text=🏍️';

// Usage in @error handler
@error="$event.target.src = 'https://via.placeholder.com/48x48/FF5722/FFFFFF?text=🏍️'"
```

### Person/Driver Images
```javascript
// Default person image for driver widgets
const defaultPersonImage = 'https://via.placeholder.com/48x48/607D8B/FFFFFF?text=👤';

// Usage in @error handler
@error="$event.target.src = 'https://via.placeholder.com/48x48/607D8B/FFFFFF?text=👤'"
```

## Styling Guidelines

### 1. Widget Title Styling
```css
.widget-with-title {
    @apply bg-white rounded-b-lg border border-t-0 border-surface-200 shadow-sm;
}
```

### 2. Clickable Title Hover Effects
```css
.cursor-pointer:hover {
    @apply bg-surface-50 transition-colors duration-200;
}
```

### 3. Responsive Grid Layout
```css
.grid.grid-cols-1.lg\:grid-cols-2 {
    /* 1 column on mobile, 2 columns on desktop */
}

.space-y-6 > * + * {
    margin-top: 1.5rem;
}
```

## API Integration Preparation

### 1. Widget Props Structure
```javascript
const props = defineProps({
    dealerId: {
        type: String,
        default: '12284'
    },
    dateFrom: {
        type: String,
        required: true
    },
    dateTo: {
        type: String,
        required: true
    }
});
```

### 2. API Call Pattern
```javascript
const fetchData = async (page = 1, perPage = 20) => {
    try {
        // TODO: Replace with real API call
        // const response = await axios.get('/api/v1/dashboard/endpoint', {
        //     params: {
        //         dealer_id: effectiveDealerId.value,
        //         date_from: props.dateFrom,
        //         date_to: props.dateTo,
        //         page: page,
        //         per_page: perPage
        //     }
        // });
        
        // Use mock data for now
        await new Promise(resolve => setTimeout(resolve, 1000));
        // Process mock data...
        
    } catch (err) {
        console.error('Error fetching data:', err);
        error.value = 'Failed to fetch data';
    }
};
```

## Next Steps for New Sub-Dashboards

### 1. Planning Phase
- Identify the main dashboard widget that needs a detail view
- Define the 2-column layout requirements
- Specify which widgets to reuse and which to create new

### 2. Implementation Checklist
- [ ] Add navigation function to main Dashboard.vue
- [ ] Make widget title clickable with hover effects
- [ ] Add new route to router configuration
- [ ] Create new detail view component
- [ ] Implement 2-column responsive layout
- [ ] Reuse existing status widget (left column, row 1)
- [ ] Create new Top5 widget (left column, row 2)
- [ ] Create new data history widget (right column)
- [ ] Add date filter functionality
- [ ] Prepare API integration structure
- [ ] Test navigation and layout
- [ ] Update documentation

### 3. Future Enhancements
- Real API integration
- Advanced filtering capabilities
- Export functionality
- Real-time data updates
- Mobile optimization improvements

## File Locations

### Views
- `web/src/views/Dashboard.vue` - Main dashboard
- `web/src/views/ProspectingActivity.vue` - Prospecting detail
- `web/src/views/UnitInboundDetail.vue` - Unit inbound detail

### Components
- `web/src/components/dashboard/` - All dashboard widgets
- `web/src/router/index.js` - Route configurations

### Documentation
- `docs/DASHBOARD_NAVIGATION_GUIDE.md` - This document
- `docs/DASHBOARD_INTEGRATION_GUIDE.md` - API integration guide
- `docs/DASHBOARD_BEST_PRACTICES.md` - Development best practices

---

*Last Updated: 2025-07-02*
*Version: 1.0*
