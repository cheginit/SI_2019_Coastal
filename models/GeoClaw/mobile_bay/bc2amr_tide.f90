! :::::::::: bc2amr ::::::::::::::::::::::::::::::::::::::::::::::;
!> \callgraph
!! \callergraph
!!  Take a grid patch with mesh widths **hx**,**hy**, of dimensions **nrow** by
!!  **ncol**,  and set the values of any piece of
!!  of the patch which extends outside the physical domain 
!!  using the boundary conditions. 
!!
!!  
!!   Specific to geoclaw:  extrapolates aux(i,j,1) at boundaries
!!   to constant.
!!
!!  ### Standard boundary condition choices for amr2ez in clawpack
!!
!!  At each boundary  k = 1 (left),  2 (right),  3 (bottom), 4 (top):
!!
!!  mthbc(k) =  
!!  * 0  for user-supplied BC's (must be inserted!)
!!  * 1  for zero-order extrapolation
!!  * 2  for periodic boundary conditions
!!  * 3  for solid walls, assuming this can be implemented
!!                   by reflecting the data about the boundary and then
!!                   negating the 2'nd (for k=1,2) or 3'rd (for k=3,4)
!!                   component of q.
!!  * 4  for sphere bcs (left half maps to right half of same side, and vice versa), as if domain folded in half
!!
!!  The corners of the grid patch are at 
!!     (xlo_patch,ylo_patch)  --  lower left corner
!!     (xhi_patch,yhi_patch) --  upper right corner
!!
!!  The physical domain itself is a rectangle bounded by
!!     (xlower,ylower)  -- lower left corner
!!     (xupper,yupper)  -- upper right corner
!!  
!   This figure below does not work with doxygen
!   the picture is the following: 
!  ____________________________________________________
! 
!                _____________________ (xupper,yupper)
!               |                     |  
!           ____|____ (xhi_patch,yhi_patch)   
!           |   |    |                |
!           |   |    |                |
!           |   |    |                |
!           |___|____|                |
!  (xlo_patch,ylo_patch) |            |
!               |                     |
!               |_____________________|   
!    (xlower,ylower)
!  ____________________________________________________
!!
!!
!>  Any cells that lie outside the physical domain are ghost cells whose
!!  values should be set in this routine.  This is tested for by comparing
!!  xlo_patch with xlower to see if values need to be set at the left
!   as in the figure above, 
!
!>  and similarly at the other boundaries.
!!  Patches are guaranteed to have at least 1 row of cells filled
!!  with interior values so it is possible to extrapolate. 
!!  Fix [trimbd()](@ref trimbd) if you want more than 1 row pre-set.
!!
!!  Make sure the order the boundaries are specified is correct
!!  so that diagonal corner cells are also properly taken care of.
!!
!!  Periodic boundaries are set before calling this routine, so if the
!!  domain is periodic in one direction only you
!!  can safely extrapolate in the other direction. 
!!
!!  Don't overwrite ghost cells in periodic directions!
!!
!! \param val data array for solution \f$q \f$ (cover the whole grid **msrc**)
!! \param aux data array for auxiliary variables 
!! \param nrow number of cells in *i* direction on this grid
!! \param ncol number of cells in *j* direction on this grid
!! \param meqn number of equations for the system
!! \param naux number of auxiliary variables
!! \param hx spacing (mesh size) in *i* direction
!! \param hy spacing (mesh size) in *j* direction
!! \param level AMR level of this grid
!! \param time setting ghost cell values at time **time**
!! \param xlo_patch left bound of the input grid
!! \param xhi_patch right bound of the input grid 
!! \param ylo_patch lower bound of the input grid 
!! \param yhi_patch upper bound of the input grid 
! ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::;

subroutine bc2amr(val,aux,nrow,ncol,meqn,naux, hx, hy, level, time,   &
                  xlo_patch, xhi_patch, ylo_patch, yhi_patch) 

    use amr_module, only: mthbc, xlower, ylower, xupper, yupper
    use amr_module, only: xperdom,yperdom,spheredom

    implicit none

    ! Input/Output
    integer, intent(in) :: nrow, ncol, meqn, naux, level
    real(kind=8), intent(in) :: hx, hy, time
    real(kind=8), intent(in) :: xlo_patch, xhi_patch
    real(kind=8), intent(in) :: ylo_patch, yhi_patch
    real(kind=8), intent(in out) :: val(meqn, nrow, ncol)
    real(kind=8), intent(in out) :: aux(naux, nrow, ncol)
    
    ! Local storage
    integer :: i, j, ibeg, jbeg, nxl, nxr, nyb, nyt, iunit, istat, cntr
    real(kind=8) :: hxmarg, hymarg
    
    integer :: iunit_wl, n_rows
    real(kind=8), dimension (:,:), allocatable :: data_array
    real(kind=8), dimension (:), allocatable :: time_input, water_level
    real(kind=8) :: tmp, y
    character(len=255) :: data_dir

    hxmarg = hx * .01d0
    hymarg = hy * .01d0

    ! Use periodic boundary condition specialized code only, if only one 
    ! boundary is periodic we still proceed below
    if (xperdom .and. (yperdom .or. spheredom)) then
        return
    end if

    ! Each check has an initial check to ensure that the boundary is a real
    ! boundary condition and otherwise skips the code.  Otherwise 
    !-------------------------------------------------------
    ! Left boundary:
    !-------------------------------------------------------
    if (xlo_patch < xlower-hxmarg) then
        ! number of grid cells from this patch lying outside physical domain:
        nxl = int((xlower + hxmarg - xlo_patch) / hx)

        select case(mthbc(1))
            case(0) ! User defined boundary condition
                ! Replace this code with a user defined boundary condition
                stop "A user defined boundary condition was not provided."
            case(1) ! Zero-order extrapolation
                do j = 1, ncol
                    do i=1, nxl
                        aux(:, i, j) = aux(:, nxl + 1, j)
                        val(:, i, j) = val(:, nxl + 1, j)
                    end do
                end do

            case(2) ! Periodic boundary condition
                continue

            case(3) ! Wall boundary conditions
                do j = 1, ncol
                    do i=1, nxl
                        aux(:, i, j) = aux(:, 2 * nxl + 1 - i, j)
                        val(:, i, j) = val(:, 2 * nxl + 1 - i, j)
                    end do
                end do
                ! negate the normal velocity:
                do j = 1, ncol
                    do i=1, nxl
                        val(2, i, j) = -val(2, i, j)
                    end do
                end do

            case(4) ! Spherical domain
                continue

            case default
                print *, "Invalid boundary condition requested."
                stop
        end select
    end if

    !-------------------------------------------------------
    ! Right boundary:
    !-------------------------------------------------------
    if (xhi_patch > xupper+hxmarg) then

        ! number of grid cells lying outside physical domain:
        nxr = int((xhi_patch - xupper + hxmarg) / hx)
        ibeg = max(nrow - nxr + 1, 1)

        select case(mthbc(2))
            case(0) ! User defined boundary condition
                ! Replace this code with a user defined boundary condition
                stop "A user defined boundary condition was not provided."
            case(1) ! Zero-order extrapolation
                do i = ibeg, nrow
                    do j = 1, ncol
                        aux(:, i, j) = aux(:, ibeg - 1, j)
                        val(:, i, j) = val(:, ibeg - 1, j)
                    end do
                end do

            case(2) ! Periodic boundary condition
                continue

            case(3) ! Wall boundary conditions
                do i=ibeg, nrow
                    do j = 1, ncol
                        aux(:, i, j) = aux(:, 2 * ibeg - 1 - i, j)
                        val(:, i, j) = val(:, 2 * ibeg - 1 - i, j)
                    end do
                end do
                ! negate the normal velocity:
                do i = ibeg, nrow
                    do j = 1, ncol
                        val(2, i, j) = -val(2, i, j)
                    end do
                end do

            case(4) ! Spherical domain
                continue

            case default
                print *, "Invalid boundary condition requested."
                stop

        end select
    end if

    !-------------------------------------------------------
    ! Bottom boundary:
    !-------------------------------------------------------
    if (ylo_patch < ylower - hymarg) then

        ! number of grid cells lying outside physical domain:
        nyb = int((ylower + hymarg - ylo_patch) / hy)

        select case(mthbc(3))
            case(0) ! User defined boundary condition
                iunit_wl = 10
                call getenv("DATA_DIR", data_dir)
                open(iunit_wl, file=trim(adjustl(data_dir))//'/water_level.bc', status='OLD', iostat=istat)

                rewind(iunit_wl)
                n_rows = 0
                do
                    read(iunit_wl, *, iostat=istat) tmp
                    if (is_iostat_end(istat)) exit
                    n_rows = n_rows + 1
                end do

                allocate(data_array(n_rows, 2))
                allocate(time_input(n_rows))
                allocate(water_level(n_rows))

                rewind(iunit_wl)
                do i= 1, n_rows
                    read(iunit_wl, *, iostat=istat) data_array(i,:)
                end do

                close(unit=iunit_wl, iostat=istat)

                time_input(:) = data_array(:,1)
                water_level(:) = data_array(:,2)

                deallocate(data_array)

                do i = 2, n_rows
                    if ((time > time_input(i-1)) .and. (time < time_input(i))) then
                        call parabola_val2(n_rows, time_input, water_level, i, time, y)
                        exit
                    end if
                end do

                deallocate(time_input)
                deallocate(water_level)

                do j = 1, nyb
                    do i = 1, nrow
                        aux(:,i,j) = aux(:, i, nyb + 1)
                        val(:,i,j) = y
                    end do
                end do
                ! Replace this code with a user defined boundary condition
                ! stop "A user defined boundary condition was not provided."
            
            case(1) ! Zero-order extrapolation
                do j = 1, nyb
                    do i = 1, nrow
                        aux(:,i,j) = aux(:, i, nyb + 1)
                        val(:,i,j) = val(:, i, nyb + 1)
                    end do
                end do

            case(2) ! Periodic boundary condition
                continue

            case(3) ! Wall boundary conditions
                do j = 1, nyb
                    do i = 1, nrow
                        aux(:,i,j) = aux(:, i, 2 * nyb + 1 - j)
                        val(:,i,j) = val(:, i, 2 * nyb + 1 - j)
                    end do
                end do
                ! negate the normal velocity:
                do j = 1, nyb
                    do i = 1, nrow
                        val(3,i,j) = -val(3, i, j)
                    end do
                end do

            case(4) ! Spherical domain
                continue

            case default
                print *, "Invalid boundary condition requested."
                stop

        end select
    end if

    !-------------------------------------------------------
    ! Top boundary:
    !-------------------------------------------------------
    if (yhi_patch > yupper + hymarg) then

        ! number of grid cells lying outside physical domain:
        nyt = int((yhi_patch - yupper + hymarg) / hy)
        jbeg = max(ncol - nyt + 1, 1)

        select case(mthbc(4))
            case(0) ! User defined boundary condition
                ! Replace this code with a user defined boundary condition
                stop "A user defined boundary condition was not provided."

            case(1) ! Zero-order extrapolation
                do j = jbeg, ncol
                    do i = 1, nrow
                        aux(:, i, j) = aux(:, i, jbeg - 1)
                        val(:, i, j) = val(:, i, jbeg - 1)
                    end do
                end do

            case(2) ! Periodic boundary condition
                continue

            case(3) ! Wall boundary conditions
                do j = jbeg, ncol 
                    do i = 1, nrow
                        aux(:, i, j) = aux(:, i, 2 * jbeg - 1 - j)
                        val(:, i, j) = val(:, i, 2 * jbeg - 1 - j)
                    end do
                end do
                ! negate the normal velocity:
                do j = jbeg, ncol
                    do i = 1, nrow
                        val(3, i, j) = -val(3, i, j)
                    end do
                end do

            case(4) ! Spherical domain
                continue

            case default
                print *, "Invalid boundary condition requested."
                stop

        end select
    end if

end subroutine bc2amr

subroutine parabola_val2(ndata, tdata, ydata, left, tval, yval)

!*****************************************************************************80
!
!! PARABOLA_VAL2 evaluates a parabolic interpolant through tabular data.
!
!  Discussion:
!
!    This routine is a utility routine used by OVERHAUSER_SPLINE_VAL.
!    It constructs the parabolic interpolant through the data in
!    3 consecutive entries of a table and evaluates this interpolant
!    at a given abscissa value.
!
!  Licensing:
!
!    This code is distributed under the GNU LGPL license.
!
!  Modified:
!
!    26 January 2004
!
!  Author:
!
!    John Burkardt
!
!  Parameters:
!
!    Input, integer ( kind = 4 ) NDATA, the number of data points.
!    NDATA must be at least 3.
!
!    Input, real ( kind = 8 ) TDATA(NDATA), the abscissas of the data
!    points.  The values in TDATA must be in strictly ascending order.
!
!    Input, real ( kind = 8 ) YDATA(DIM_NUM,NDATA), the data points
!    corresponding to the abscissas.
!
!    Input, integer ( kind = 4 ) LEFT, the location of the first of the three
!    consecutive data points through which the parabolic interpolant
!    must pass.  1 <= LEFT <= NDATA - 2.
!
!    Input, real ( kind = 8 ) TVAL, the value of T at which the parabolic
!    interpolant is to be evaluated.  Normally, TDATA(1) <= TVAL <= T(NDATA),
!    and the data will be interpolated.  For TVAL outside this range,
!    extrapolation will be used.
!
!    Output, real ( kind = 8 ) YVAL(DIM_NUM), the value of the parabolic
!    interpolant at TVAL.
!
  implicit none

  integer ( kind = 4 ) ndata

  real ( kind = 8 ) dif1
  real ( kind = 8 ) dif2
  integer ( kind = 4 ) i
  integer ( kind = 4 ) left
  real ( kind = 8 ) t1
  real ( kind = 8 ) t2
  real ( kind = 8 ) t3
  real ( kind = 8 ) tval
  real ( kind = 8 ) tdata(ndata)
  real ( kind = 8 ) ydata(ndata)
  real ( kind = 8 ) y1
  real ( kind = 8 ) y2
  real ( kind = 8 ) y3
  real ( kind = 8 ) yval
!
!  Check.
!
  if ( left < 1 ) then
    write ( *, '(a)' ) ' '
    write ( *, '(a)' ) 'PARABOLA_VAL2 - Fatal error!'
    write ( *, '(a)' ) '  LEFT < 1.'
    write ( *, '(a,i8)' ) '  LEFT = ', left
    stop 1
  end if

  if ( ndata-2 < left ) then
    write ( *, '(a)' ) ' '
    write ( *, '(a)' ) 'PARABOLA_VAL2 - Fatal error!'
    write ( *, '(a)' ) '  NDATA-2 < LEFT.'
    write ( *, '(a,i8)' ) '  NDATA = ', ndata
    write ( *, '(a,i8)' ) '  LEFT =  ', left
    stop 1
  end if
!
!  Copy out the three abscissas.
!
  t1 = tdata(left)
  t2 = tdata(left+1)
  t3 = tdata(left+2)

  if ( t2 <= t1 .or. t3 <= t2 ) then
    write ( *, '(a)' ) ' '
    write ( *, '(a)' ) 'PARABOLA_VAL2 - Fatal error!'
    write ( *, '(a)' ) '  T2 <= T1 or T3 <= T2.'
    stop 1
  end if
!
!  Construct and evaluate a parabolic interpolant for the data
!  in each dimension.
!

  y1 = ydata(left)
  y2 = ydata(left+1)
  y3 = ydata(left+2)

  dif1 = ( y2 - y1 ) / ( t2 - t1 )
  dif2 = ( ( y3 - y1 ) / ( t3 - t1 ) &
       - ( y2 - y1 ) / ( t2 - t1 ) ) / ( t3 - t2 )
  yval = y1 + ( tval - t1 ) * ( dif1 + ( tval - t2 ) * dif2 )

  return
end subroutine parabola_val2
