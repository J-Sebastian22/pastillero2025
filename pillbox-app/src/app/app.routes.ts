import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { Medicamentos } from './pages/medicamentos/medicamentos';
import { Horarios } from './pages/horarios/horarios';
import { Dispositivo } from './services/dispositivo';
import { Registro } from './pages/registro/registro';



export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: Login },
  { path: 'registro', component: Registro },
  { path: 'dashboard', component: Dashboard },
  { path: 'medicamentos', component: Medicamentos },
  { path: 'horarios', component: Horarios },
  { path: 'dispositivo', component: Dispositivo }
];
