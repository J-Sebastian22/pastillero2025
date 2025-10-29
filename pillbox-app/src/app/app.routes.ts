import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { Medicamentos } from './pages/medicamentos/medicamentos';
import { Horarios } from './pages/horarios/horarios';
import { Dispositivo } from './services/dispositivo';
import { Registro } from './pages/registro/registro';
import { MainLayout } from './pages/layout/main-layout';



export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },

  // Login y Registro siguen fuera del layout
  { path: 'login', loadComponent: () => import('./pages/login/login').then(m => m.Login) },
  { path: 'registro', loadComponent: () => import('./pages/registro/registro').then(m => m.Registro) },

  // Sección interna protegida con layout
  {
    path: '',
    component: MainLayout,
    children: [
      { path: 'dashboard', component: Dashboard },
      { path: 'medicamentos', component: Medicamentos },
      { path: 'horarios', component: Horarios },
    ]
  }
];